import { useState } from 'react';

export default function App() {
  const models = [
    {
      name: "fal-mc",
      version: "0.2.1",
      desc: "Fal.ai client model"
    },
    {
      name: "fal-audio-gen-musical-memex", 
      version: "1.0.0",
      desc: "Musical generation model"
    }
  ];

  const [results, setResults] = useState<{[key: string]: string | null}>({});
  const [loading, setLoading] = useState<string[]>([]);

  async function callModel(modelName: string) {
    // Clear previous results for this model
    setResults(prev => ({ ...prev, [modelName]: null }));
    
    try {
      // Use MCP tool to invoke the model
      const result = await window.mcpApp.invokeTool(modelName);
      
      // Display result
      setResults(prev => ({ 
        ...prev, 
        [modelName]: JSON.stringify(result?.output || result || 'Result unavailable', null, 2) 
      }));
    } catch (error) {
      console.error(`Failed to call ${modelName}:`, error);
    } finally {
      setLoading(prev => prev.filter(m => m !== modelName));
    }
  }

  function handleModelClick(model: typeof models[0]) {
    if (!loading.includes(model.name)) {
      setLoading(prev => [...prev, model.name]);
    }
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Fal MCP Server</h1>
        <p style={styles.subtitle}>AI Model Server via fal.ai API</p>
      </header>

      {models.map(model => (
        <div 
          key={model.name}
          onClick={() => handleModelClick(model)}
          style={{
            ...styles.card,
            opacity: loading.includes(model.name) ? 0.7 : 1,
            cursor: loading.includes(model.name) ? 'not-allowed' : 'pointer'
          }}
        >
          <div style={styles.cardHeader}>
            <h3 style={styles.modelName}>{model.name}</h3>
            <span style={{
              ...styles.statusBadge,
              backgroundColor: loading.includes(model.name) 
                ? '#fef3c7' // amber
                : results[model.name] !== null 
                  ? '#d1fae5' // green
                  : '#dbeafe', // blue
              color: loading.includes(model.name) 
                ? '#92400e' 
                : results[model.name] !== null 
                  ? '#065f46' 
                  : '#1e40af'
            }}>
              {loading.includes(model.name) ? 'Running...' : 
               results[model.name] !== null ? 'Success' : 'Ready'}
            </span>
          </div>

          <p style={styles.description}>{model.desc}</p>

          <button 
            style={{
              ...styles.button,
              opacity: loading.includes(model.name) ? 0.5 : 1
            }}
            onClick={(e) => {
              e.stopPropagation();
              handleModelClick(model);
            }}
            disabled={loading.includes(model.name)}
          >
            Call Model
          </button>

          {results[model.name] !== null && (
            <div style={styles.output}>
              <strong>{model.name} Result:</strong>
              <pre style={styles.pre}>{results[model.name]}</pre>
            </div>
          )}
        </div>
      ))}

      {models.length === 0 && (
        <p style={styles.emptyMessage}>No models available yet. Checking connectivity...</p>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
    padding: '2rem 1rem'
  },
  header: {
    textAlign: 'center',
    marginBottom: '2rem',
    color: '#1f2937'
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '0.5rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent'
  },
  subtitle: {
    color: '#6b7280',
    fontSize: '1.1rem'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '1.5rem',
    marginBottom: '1rem',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s'
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '0.5rem'
  },
  modelName: {
    margin: 0,
    flex: 1,
    color: '#374151'
  },
  statusBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    fontSize: '0.85rem',
    fontWeight: 600,
    marginLeft: '0.75rem'
  },
  description: {
    margin: '0 0 1rem 0',
    color: '#6b7280',
    fontSize: '0.95rem'
  },
  button: {
    width: '100%',
    padding: '0.75rem',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: 600,
    cursor: 'pointer'
  },
  output: {
    marginTop: '1rem',
    padding: '1rem',
    backgroundColor: '#f9fafb',
    border radius: '8px',
    overflowWrap: 'break-word'
  },
  pre: {
    margin: 0,
    backgroundColor: '#f3f4f6',
    padding: '0.5rem',
    borderRadius: '6px',
    whiteSpace: 'pre-wrap',
    fontSize: '0.875rem'
  },
  emptyMessage: {
    textAlign: 'center',
    color: '#6b7280'
  }
};
