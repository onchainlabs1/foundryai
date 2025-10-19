export default function CSSTestPage() {
  return (
    <div className="min-h-screen bg-blue-500 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-4">
          🎨 CSS Test Page
        </h1>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Se você vê estilos, o CSS está funcionando!
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-100 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-red-800">Card 1</h3>
              <p className="text-red-600">Fundo vermelho claro</p>
            </div>
            <div className="bg-green-100 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-green-800">Card 2</h3>
              <p className="text-green-600">Fundo verde claro</p>
            </div>
            <div className="bg-blue-100 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-blue-800">Card 3</h3>
              <p className="text-blue-600">Fundo azul claro</p>
            </div>
          </div>
          <div className="mt-6">
            <button className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
              Botão de Teste
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
