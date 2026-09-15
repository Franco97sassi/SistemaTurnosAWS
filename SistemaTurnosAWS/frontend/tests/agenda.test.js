import assert from "node:assert/strict";
import test from "node:test";

import { appointmentStats, initials } from "../src/lib/agenda.js";

test("summarizes appointments for the dashboard", () => {
  const items = [
    { estado: "pendiente", fecha: "2035-05-10T10:00:00Z" },
    { estado: "cancelado", fecha: "2035-05-11T10:00:00Z" },
  ];
  assert.deepEqual(appointmentStats(items, new Date("2035-05-10T18:00:00Z")), {
    pendientes: 1,
    cancelados: 1,
    hoy: 1,
  });
});

test("builds a compact patient avatar", () => {
  assert.equal(initials("Ada Lovelace"), "AL");
  assert.equal(initials("  Grace   Brewster Murray Hopper "), "GB");
});
