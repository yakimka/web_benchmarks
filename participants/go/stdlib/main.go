package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/jackc/pgx/v4/pgxpool"
)

func apiHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	queryValue := r.URL.Query().Get("query")
	headerValue := r.Header.Get("X-Header")
	data := map[string]string{
		"message":     "Hello, world!",
		"from_query":  queryValue,
		"from_header": headerValue,
	}

	json.NewEncoder(w).Encode(data)
}

func plaintextHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write([]byte("Hello, world!"))
}

var pool *pgxpool.Pool

type User struct {
	ID           int       `json:"id"`
	Username     string    `json:"username"`
	Email        string    `json:"email"`
	PasswordHash string    `json:"password_hash"`
	CreatedAt    time.Time `json:"created_at"`
	IsActive     bool      `json:"is_active"`
}

type Device struct {
	ID              int        `json:"id"`
	UserID          int        `json:"user_id"`
	DeviceName      string     `json:"device_name"`
	DeviceType      *string    `json:"device_type"`
	SerialNumber    string     `json:"serial_number"`
	IPAddress       *string    `json:"ip_address"`
	MACAddress      *string    `json:"mac_address"`
	Status          string     `json:"status"`
	LastOnline      *time.Time `json:"last_online"`
	PurchaseDate    *time.Time `json:"purchase_date"`
	WarrantyExpiry  *time.Time `json:"warranty_expiry"`
	Location        *string    `json:"location"`
	FirmwareVersion *string    `json:"firmware_version"`
	CreatedAt       time.Time  `json:"created_at"`
}

func initPool() error {
	dbURL := os.Getenv("DATABASE_URL")
	config, err := pgxpool.ParseConfig(dbURL)
	if err != nil {
		return err
	}

	pool, err = pgxpool.ConnectConfig(context.Background(), config)
	return err
}

func dbHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	// Fetch user data
	userRows, err := pool.Query(ctx, "SELECT * FROM users WHERE id = $1", 1)
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("Error querying user: %v", err)
		return
	}
	defer userRows.Close()

	var user User
	if userRows.Next() {
		err = userRows.Scan(
			&user.ID,
			&user.Username,
			&user.Email,
			&user.PasswordHash,
			&user.CreatedAt,
			&user.IsActive,
		)
		if err != nil {
			http.Error(w, "Error scanning user data", http.StatusInternalServerError)
			log.Printf("Error scanning user: %v", err)
			return
		}
	}

	deviceRows, err := pool.Query(ctx, "SELECT * FROM devices LIMIT 10")
	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Printf("Error querying devices: %v", err)
		return
	}
	defer deviceRows.Close()

	var devices []Device
	for deviceRows.Next() {
		var device Device
		err = deviceRows.Scan(
			&device.ID,
			&device.UserID,
			&device.DeviceName,
			&device.DeviceType,
			&device.SerialNumber,
			&device.IPAddress,
			&device.MACAddress,
			&device.Status,
			&device.LastOnline,
			&device.PurchaseDate,
			&device.WarrantyExpiry,
			&device.Location,
			&device.FirmwareVersion,
			&device.CreatedAt,
		)
		if err != nil {
			http.Error(w, "Error scanning device data", http.StatusInternalServerError)
			log.Printf("Error scanning device: %v", err)
			return
		}
		devices = append(devices, device)
	}

	w.Header().Set("Content-Type", "application/json")

	if err := json.NewEncoder(w).Encode(devices); err != nil {
		http.Error(w, "Error encoding response", http.StatusInternalServerError)
		log.Printf("Error encoding response: %v", err)
		return
	}
}

func main() {
	if err := initPool(); err != nil {
		log.Fatalf("Error initializing pool: %v", err)
	}
	defer pool.Close()

	http.HandleFunc("GET /api", apiHandler)
	http.HandleFunc("GET /plaintext", plaintextHandler)
	http.HandleFunc("GET /db", dbHandler)

	log.Println("Server starting on :8000")
	if err := http.ListenAndServe(":8000", nil); err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
