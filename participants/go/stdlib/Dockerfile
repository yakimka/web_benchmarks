FROM golang:1.23 AS builder
WORKDIR /go
COPY . .
RUN CGO_ENABLED=0 go build

FROM alpine:latest
WORKDIR /app
COPY --from=builder /go/app .
EXPOSE 8000
CMD ["./app"]
