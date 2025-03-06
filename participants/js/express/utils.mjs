import { sjs, attr } from "slow-json-stringify";

export const headerTypes = {
  plain: "text/plain",
  json: "application/json",
  html: "text/html; charset=UTF-8",
};

export function writeResponse(res, text, type = headerTypes["json"]) {
  res.writeHead(200, {
    "content-type": type,
    server: "Express",
  });
  res.end(text);
}

export function handleError(error, response) {
  console.error(error);
  response.end("Internal Server Error");
}

export const jsonSerializer = sjs({ message: attr("string") });
export const userObjectSerializer = sjs({
  id: attr("number"),
  username: attr("string"),
  email: attr("string"),
  password_hash: attr("string"),
  created_at: attr("string", (value) => value ? value.toLocaleString() : undefined),
  is_active: attr("boolean"),
});
