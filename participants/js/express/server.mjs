import express from "express";
import {
  handleError,
  jsonSerializer,
  userObjectSerializer,
  writeResponse,
  headerTypes,
} from "./utils.mjs";

let db = await import("./postgres.mjs");

const app = express();

app.get("/plaintext", (req, res) => {
  writeResponse(res, "Hello, World!", headerTypes["plain"]);
});

app.get("/api", (req, res) => {
  writeResponse(res, jsonSerializer({ message: "Hello, World!" }));
});

app.get("/db", async (req, res) => {
try {
  const user = await db.user();
  const serializedUser = userObjectSerializer(user);
  const devices = await db.devices();
  writeResponse(res, JSON.stringify(devices));
} catch (error) {
  handleError(error, res);
}
});

app.all("*", (req, res) => {
  res.status(404).send("Not Found");
});

const host = process.env.HOST || "0.0.0.0";
const port = parseInt(process.env.PORT || "8000");
app.listen(port, host, () => {
  console.log(`Server running at http://${host}:${port}/`);
});
