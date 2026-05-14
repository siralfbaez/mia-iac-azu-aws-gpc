package main

import (
	"context"
	"log"
	"os"
	"mia-iac-azu-aws-gpc/pkg/elastic-client-wrapper"
)

func main() {
	log.Println("Starting Mia Search-Ingest-Agent (Go Nervous System)...")

	// Load credentials from your "Security Shield" .env
	cloudID := os.Getenv("ELASTIC_CLOUD_ID")
	apiKey := os.Getenv("ELASTIC_API_KEY")

	client, err := elasticwrapper.NewSearchClient(cloudID, apiKey)
	if err != nil {
		log.Fatalf("Error creating Elastic client: %s", err)
	}

	// Mocking a Kafka Stream from your SBA project experience
	// In a real scenario, this would be a loop consuming from Kafka
	mockStream := []interface{}{
		map[string]interface{}{
			"doc_id": "SBA-KAFKA-001",
			"title":  "Compliance Audit Log - Q1",
			"source_system": "Unisys_Mainframe",
			"_iam_access_control": []string{"admin", "auditor"},
		},
	}

	err = client.BulkIndex(context.Background(), "enterprise-knowledge-v1", mockStream)
	if err != nil {
		log.Printf("Bulk Indexing failed: %s", err)
	}

	log.Println("Successfully indexed legacy stream to Elastic.")
}