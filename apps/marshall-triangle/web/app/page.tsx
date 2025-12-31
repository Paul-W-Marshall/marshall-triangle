
import TriangleCanvas from '@/components/TriangleCanvas'

export default function Home() {
  return (
    <main className="relative w-full h-screen bg-black">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-10 flex justify-between items-center p-4">
        <h1 className="text-2xl font-bold text-white">
          Marshall Triangle (Preview)
        </h1>
        <a
          href="https://github.com/Paul-W-Marshall/marshall-triangle"
          target="_blank"
          rel="noopener noreferrer"
          className="text-white hover:text-gray-300 transition-colors"
        >
          GitHub
        </a>
      </header>

      {/* Canvas */}
      <TriangleCanvas />
    </main>
  )
}
