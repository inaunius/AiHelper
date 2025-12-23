import { useState, useEffect } from 'react'
import { Calendar, ExternalLink, FileText, AlertCircle, Clock, RefreshCw, FileWarning, Copy } from 'lucide-react'

interface LawChange {
  id: number
  title: string
  url: string
  date: string
  description: string
}

function formatDate(pubDate: string): string {
  try {
    const date = new Date(pubDate)
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })
  } catch {
    return pubDate
  }
}

function App() {
  const [changes, setChanges] = useState<LawChange[]>([])
  const [report, setReport] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [reportLoading, setReportLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const fetchChanges = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/changes')
      if (!res.ok) throw new Error()
      const data = await res.json()
      setChanges(data)
    } catch (err) {
      alert('Ошибка подключения к бэкенду. Убедись, что uvicorn запущен!')
    }
    setLoading(false)
  }

  const generateReport = async () => {
    setReportLoading(true)
    setReport(null)
    try {
      const res = await fetch('http://localhost:8000/api/generate-report', { method: 'POST' })
      const data = await res.json()
      setReport(data.report_text)
    } catch (err) {
      setReport('Ошибка генерации отчёта')
    }
    setReportLoading(false)
  }

  const copyReport = () => {
    if (report) {
      navigator.clipboard.writeText(report)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  useEffect(() => {
    fetchChanges()
  }, [])

  const isCritical = (text: string) => {
    const keywords = ['ндфл', 'взносы', 'зуп', 'приказ', 'федеральный закон', 'постановление', 'фнс', 'минтруд', 'изменение']
    return keywords.some(kw => text.toLowerCase().includes(kw))
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="bg-gradient-to-r from-gazprom-dark via-gazprom-blue to-gazprom-dark text-white shadow-2xl">
        <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <img src="frontend/src/assets/img/Gazprom_Neft_Logo.png" alt="Газпромнефть" className="h-16" />
            <div>
              <h1 className="text-3xl font-bold">AI-помощник</h1>
              <p className="text-xl opacity-90">Мониторинг изменений законодательства РФ и 1С:ЗУП 3.1</p>
            </div>
          </div>
          <button onClick={fetchChanges} className="bg-white/20 backdrop-blur px-6 py-3 rounded-xl font-medium hover:bg-white/30 flex items-center gap-3 transition">
            <RefreshCw className="w-5 h-5" /> Обновить
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="bg-white/80 backdrop-blur rounded-2xl shadow-xl p-8 border border-gazprom-blue/20 transition hover:scale-105">
            <div className="flex items-center gap-4 mb-4">
              <FileText className="w-10 h-10 text-gazprom-blue" />
              <p className="text-gray-600">Всего изменений</p>
            </div>
            <p className="text-5xl font-bold text-gazprom-blue">{changes.length}</p>
          </div>
          <div className="bg-white/80 backdrop-blur rounded-2xl shadow-xl p-8 border border-red-200 transition hover:scale-105">
            <div className="flex items-center gap-4 mb-4">
              <FileWarning className="w-10 h-10 text-red-600" />
              <p className="text-gray-600">Критических</p>
            </div>
            <p className="text-5xl font-bold text-red-600">{changes.filter(c => isCritical(c.title + c.description)).length}</p>
          </div>
          <div className="bg-white/80 backdrop-blur rounded-2xl shadow-xl p-8 border border-gazprom-blue/20 transition hover:scale-105">
            <div className="flex items-center gap-4 mb-4">
              <Calendar className="w-10 h-10 text-gazprom-blue" />
              <p className="text-gray-600">Источник</p>
            </div>
            <p className="text-3xl font-bold text-gazprom-blue">Консультант+</p>
          </div>
          <div className="bg-white/80 backdrop-blur rounded-2xl shadow-xl p-8 border border-gazprom-blue/20 transition hover:scale-105">
            <div className="flex items-center gap-4 mb-4">
              <Clock className="w-10 h-10 text-gazprom-blue" />
              <p className="text-gray-600">Последнее обновление</p>
            </div>
            <p className="text-3xl font-bold">{new Date().toLocaleDateString('ru-RU')}</p>
          </div>
        </div>
        <div className="text-center mb-16">
          <button
            onClick={generateReport}
            disabled={reportLoading}
            className="bg-gradient-to-r from-gazprom-blue to-gazprom-dark text-white px-20 py-8 rounded-3xl text-2xl font-bold shadow-2xl hover:shadow-3xl transition-all flex items-center gap-6 mx-auto disabled:opacity-70"
          >
            <FileText className="w-12 h-12" />
            {reportLoading ? 'Генерируется отчёт GigaChat...' : 'Сформировать аналитический отчёт'}
          </button>
        </div>
        <div className="bg-white/90 backdrop-blur rounded-3xl shadow-2xl overflow-hidden">
          <div className="p-10 bg-gradient-to-r from-gazprom-blue/10 to-gazprom-dark/10">
            <h2 className="text-4xl font-bold text-gazprom-dark">Последние изменения</h2>
          </div>
          {loading ? (
            <div className="p-20 text-center text-2xl text-gray-500">Загрузка данных...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gazprom-blue/5">
                  <tr>
                    <th className="px-10 py-6 text-left text-lg font-semibold">Дата</th>
                    <th className="px-10 py-6 text-left text-lg font-semibold">Документ</th>
                    <th className="px-10 py-6 text-left text-lg font-semibold">Кратко</th>
                    <th className="px-10 py-6 text-left text-lg font-semibold">Статус</th>
                    <th className="px-10 py-6 text-left text-lg font-semibold">Ссылка</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {changes.map((change, index) => (
                    <tr key={change.id} className={`transition hover:bg-gazprom-blue/5 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      <td className="px-10 py-8 font-medium">{formatDate(change.date)}</td>
                      <td className="px-10 py-8 font-bold text-gazprom-blue text-lg">{change.title}</td>
                      <td className="px-10 py-8 text-gray-700">{change.description.slice(0, 200)}...</td>
                      <td className="px-10 py-8">
                        {isCritical(change.title + change.description) ? (
                          <span className="bg-red-100 text-red-700 px-6 py-3 rounded-full font-bold flex items-center gap-2">
                            <AlertCircle className="w-6 h-6" /> Критично
                          </span>
                        ) : (
                          <span className="bg-green-100 text-green-700 px-6 py-3 rounded-full font-bold flex items-center gap-2">
                            <Clock className="w-6 h-6" /> Инфо
                          </span>
                        )}
                      </td>
                      <td className="px-10 py-8">
                        <a href={change.url} target="_blank" rel="noopener noreferrer" className="text-gazprom-blue font-bold hover:underline flex items-center gap-2">
                          Открыть <ExternalLink className="w-5 h-5" />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        {report && (
          <div className="mt-20 bg-white/90 backdrop-blur rounded-3xl shadow-2xl p-12 border border-gazprom-blue/30">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-4xl font-bold text-gazprom-dark flex items-center gap-6">
                <FileText className="w-12 h-12 text-gazprom-blue" />
                Аналитический отчёт GigaChat
              </h2>
              <button onClick={copyReport} className="bg-gazprom-blue text-white px-6 py-3 rounded-xl flex items-center gap-3 hover:bg-gazprom-dark transition">
                <Copy className="w-5 h-5" /> {copied ? 'Скопировано!' : 'Копировать'}
              </button>
            </div>
            <div className="bg-gray-50 p-8 rounded-2xl text-gray-800 leading-relaxed whitespace-pre-wrap text-lg">
              {report}
            </div>
          </div>
        )}
      </main>

      <footer className="bg-gazprom-dark text-white py-10 mt-24">
        <div className="max-w-7xl mx-auto px-8 text-center">
          <p className="text-2xl font-bold">© 2025 ООО «Газпромнефть-ЦР»</p>
        </div>
      </footer>
    </div>
  )
}

export default App