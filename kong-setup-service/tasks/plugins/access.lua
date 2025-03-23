local auth_header = kong.request.get_header("Authorization")

if not auth_header then
  return kong.response.exit(401, { message = "Missing Authorization header" })
end

local _, _, token = string.find(auth_header, "Bearer%s+(.+)")
if not token then
  return kong.response.exit(401, { message = "Invalid Authorization header format" })
end

local jwt_decoder = require "kong.plugins.jwt.jwt_parser"
local jwt_obj, err = jwt_decoder:new(token)
if not jwt_obj then
  return kong.response.exit(401, { message = "Invalid JWT token: " .. err })
end

local sub = jwt_obj.claims.sub
if not sub then
  return kong.response.exit(400, { message = "'sub' claim not found in JWT" })
end

kong.service.request.set_header("auth-user-identifier", sub)