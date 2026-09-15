#!/usr/bin/env bash

# The AWS CLI services-stable waiter stops after ten minutes, even while ECS is
# still making progress. Poll the deployment itself so slow, valid Fargate
# starts do not become false-negative workflow failures.
set -euo pipefail

task_definition_arn=${1:?Usage: wait-for-ecs-deployment.sh TASK_DEFINITION_ARN}
region=${AWS_REGION:?AWS_REGION is required}
cluster=${ECS_CLUSTER:?ECS_CLUSTER is required}
service=${ECS_SERVICE:?ECS_SERVICE is required}
timeout_seconds=${ECS_DEPLOY_TIMEOUT_SECONDS:-1200}
poll_seconds=${ECS_DEPLOY_POLL_SECONDS:-15}
deadline=$((SECONDS + timeout_seconds))

diagnose() {
  echo "::group::ECS deployment diagnostics"
  aws ecs describe-services \
    --region "$region" --cluster "$cluster" --services "$service" \
    --query 'services[0].{status:status,desired:desiredCount,running:runningCount,pending:pendingCount,deployments:deployments[*].{id:id,status:status,rolloutState:rolloutState,rolloutStateReason:rolloutStateReason,taskDefinition:taskDefinition,desired:desiredCount,running:runningCount,pending:pendingCount,failedTasks:failedTasks},events:events[0:10].[createdAt,message]}' \
    --output json || true

  stopped_tasks=$(aws ecs list-tasks \
    --region "$region" --cluster "$cluster" --service-name "$service" \
    --desired-status STOPPED --max-items 10 --query 'taskArns' --output text 2>/dev/null || true)
  if [[ -n "$stopped_tasks" && "$stopped_tasks" != "None" ]]; then
    aws ecs describe-tasks \
      --region "$region" --cluster "$cluster" --tasks $stopped_tasks \
      --query 'tasks[*].{task:taskArn,taskDefinition:taskDefinitionArn,stoppedReason:stoppedReason,stopCode:stopCode,containers:containers[*].{name:name,reason:reason,exitCode:exitCode,lastStatus:lastStatus}}' \
      --output json || true
  fi
  echo "::endgroup::"
}

while ((SECONDS < deadline)); do
  service_json=$(aws ecs describe-services \
    --region "$region" --cluster "$cluster" --services "$service" \
    --query 'services[0]' --output json)

  if [[ -z "$service_json" || "$service_json" == "null" ]]; then
    echo "::error::ECS service $cluster/$service was not found."
    diagnose
    exit 1
  fi

  deployment=$(jq --compact-output --arg task "$task_definition_arn" \
    '.deployments[] | select(.taskDefinition == $task)' <<<"$service_json" | head -n 1)

  if [[ -z "$deployment" ]]; then
    echo "::error::ECS no longer reports the requested task definition; it may have rolled back."
    diagnose
    exit 1
  fi

  rollout_state=$(jq -r '.rolloutState // "IN_PROGRESS"' <<<"$deployment")
  desired=$(jq -r '.desiredCount // 0' <<<"$deployment")
  running=$(jq -r '.runningCount // 0' <<<"$deployment")
  pending=$(jq -r '.pendingCount // 0' <<<"$deployment")
  echo "ECS rollout: state=$rollout_state desired=$desired running=$running pending=$pending"

  if [[ "$rollout_state" == "COMPLETED" && "$running" -ge "$desired" && "$pending" -eq 0 ]]; then
    echo "Backend deployment completed successfully."
    exit 0
  fi

  if [[ "$rollout_state" == "FAILED" ]]; then
    reason=$(jq -r '.rolloutStateReason // "ECS deployment circuit breaker reported a failure"' <<<"$deployment")
    echo "::error::$reason"
    diagnose
    exit 1
  fi

  sleep "$poll_seconds"
done

echo "::error::ECS deployment did not complete within ${timeout_seconds} seconds."
diagnose
exit 1
