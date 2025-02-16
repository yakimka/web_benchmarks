package main

import (
	"encoding/json"
	"net/http"
)

func apiHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	queryValue := r.URL.Query().Get("query")
	headerValue := r.Header.Get("X-Header")
	data := map[string]string{
		"message":    "Hello, world!",
		"from_query": queryValue,
		"from_header": headerValue,
	}

	json.NewEncoder(w).Encode(data)
}

func plaintextHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write([]byte("Hello, world!"))
}

func main() {
	http.HandleFunc("/api", apiHandler)
	http.HandleFunc("/plaintext", plaintextHandler)

	http.ListenAndServe(":8000", nil)
}
