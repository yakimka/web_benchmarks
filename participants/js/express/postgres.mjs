import postgres from "postgres";

const sql = postgres({
  host: process.env.POSTGRES_HOST,
  user: "postgres",
  password: "postgres",
  database: "postgres",
  max: 1,
});

export const user = async () => await sql`SELECT * FROM users WHERE id = 1`;
export const devices = async () => await sql`SELECT * FROM devices LIMIT 10`;
