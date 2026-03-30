package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"

	_ "modernc.org/sqlite"
)

type Note struct {
	ID      int    `json:"id"`
	Content string `json:"content"`
}

var db *sql.DB

func main() {
	var err error
	db, err = sql.Open("sqlite", "notes.db")
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
	}
	defer db.Close()

	_, err = db.Exec(`CREATE TABLE IF NOT EXISTS notes (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		content TEXT NOT NULL
	)`)
	if err != nil {
		log.Fatalf("Error creating table: %v", err)
	}

	http.HandleFunc("/notes", notesHandler)

	log.Println("Server starting on :8080")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

func notesHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		handlePostNote(w, r)
	case http.MethodGet:
		handleGetNotes(w, r)
	default:
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusMethodNotAllowed)
		resp := map[string]string{"error": "method not allowed"}
		err := json.NewEncoder(w).Encode(resp)
		if err != nil {
			log.Printf("Error encoding method not allowed response: %v", err)
		}
	}
}

func handlePostNote(w http.ResponseWriter, r *http.Request) {
	type reqBody struct {
		Content string `json:"content"`
	}

	var nb reqBody
	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(&nb)
	if err != nil {
		log.Printf("Error decoding request body: %v", err)
		httpError(w, http.StatusBadRequest, "invalid json body")
		return
	}

	if nb.Content == "" {
		httpError(w, http.StatusBadRequest, "content cannot be empty")
		return
	}

	result, err := db.Exec("INSERT INTO notes(content) VALUES(?)", nb.Content)
	if err != nil {
		log.Printf("Error inserting note: %v", err)
		httpError(w, http.StatusInternalServerError, "failed to save note")
		return
	}

	id, err := result.LastInsertId()
	if err != nil {
		log.Printf("Error getting last insert id: %v", err)
		httpError(w, http.StatusInternalServerError, "failed to save note")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)

	resp := Note{
		ID:      int(id),
		Content: nb.Content,
	}
	err = json.NewEncoder(w).Encode(resp)
	if err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

func handleGetNotes(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query("SELECT id, content FROM notes")
	if err != nil {
		log.Printf("Error querying notes: %v", err)
		httpError(w, http.StatusInternalServerError, "failed to get notes")
		return
	}
	defer func() {
		err := rows.Close()
		if err != nil {
			log.Printf("Error closing rows: %v", err)
		}
	}()

	var notes []Note
	for rows.Next() {
		var n Note
		err := rows.Scan(&n.ID, &n.Content)
		if err != nil {
			log.Printf("Error scanning row: %v", err)
			httpError(w, http.StatusInternalServerError, "failed to get notes")
			return
		}
		notes = append(notes, n)
	}
	err = rows.Err()
	if err != nil {
		log.Printf("Rows iteration error: %v", err)
		httpError(w, http.StatusInternalServerError, "failed to get notes")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	err = json.NewEncoder(w).Encode(notes)
	if err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

func httpError(w http.ResponseWriter, status int, msg string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	resp := map[string]string{"error": msg}
	err := json.NewEncoder(w).Encode(resp)
	if err != nil {
		log.Printf("Error encoding HTTP error response: %v", err)
	}
}