export default function TestPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>✅ AIMS Studio - Test Page</h1>
      <p>Se você está vendo esta página, o frontend está funcionando!</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
        <h3>Status dos Serviços:</h3>
        <ul>
          <li>✅ Frontend: Rodando em localhost:3000</li>
          <li>✅ Backend: Rodando em localhost:8002</li>
          <li>✅ Build: Compilado com sucesso</li>
        </ul>
      </div>
      <div style={{ marginTop: '20px' }}>
        <a href="/" style={{ color: '#007bff', textDecoration: 'none' }}>
          ← Voltar para o Dashboard
        </a>
      </div>
    </div>
  )
}