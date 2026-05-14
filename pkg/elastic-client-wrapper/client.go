package elasticwrapper

import (
	"context"
	"fmt"
	"github.com/elastic/go-elasticsearch/v8"
	"github.com/elastic/go-elasticsearch/v8/esutil"
	"log"
	"time"
)

type SearchClient struct {
	client *elasticsearch.Client
}

func NewSearchClient(cloudID, apiKey string) (*SearchClient, error) {
	cfg := elasticsearch.Config{
		CloudID: cloudID,
		APIKey:  apiKey,
	}
	es, err := elasticsearch.NewClient(cfg)
	if err != nil {
		return nil, err
	}
	return &SearchClient{client: es}, nil
}

// BulkIndexer handles high-volume streams (Kafka style)
func (s *SearchClient) BulkIndex(ctx context.Context, indexName string, docs []interface{}) error {
	bi, err := esutil.NewBulkIndexer(esutil.BulkIndexerConfig{
		Index:         indexName,
		Client:        s.client,
		NumWorkers:    4, // Concurrency for performance
		FlushInterval: 500 * time.Millisecond,
	})
	if err != nil {
		return err
	}

	for _, doc := range docs {
		err = bi.Add(ctx, esutil.BulkIndexerItem{
			Action: "index",
			Body:   esutil.NewJSONReader(doc),
		})
		if err != nil {
			return err
		}
	}

	return bi.Close(ctx)
}