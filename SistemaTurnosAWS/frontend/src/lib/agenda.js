export const appointmentStats = (items, now = new Date()) => ({
  pendientes: items.filter((item) => item.estado === "pendiente").length,
  cancelados: items.filter((item) => item.estado === "cancelado").length,
  hoy: items.filter((item) => new Date(item.fecha).toDateString() === now.toDateString()).length,
});

export const initials = (name) =>
  name
    .trim()
    .split(/\s+/)
    .map((word) => word[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
