package main

import (
	"encoding/json"
	"net/http"
)

func jsonHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	data := map[string]string{"message": "Hello, world!"}
	json.NewEncoder(w).Encode(data)
}

func plaintextHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write([]byte("Hello, world!"))
}

func main() {
	http.HandleFunc("/json", jsonHandler)
	http.HandleFunc("/plaintext", plaintextHandler)

	http.ListenAndServe(":8000", nil)
}
