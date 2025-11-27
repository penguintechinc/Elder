import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

interface VillageIdBadgeProps {
  villageId: string
  className?: string
}

export default function VillageIdBadge({ villageId, className = '' }: VillageIdBadgeProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await navigator.clipboard.writeText(villageId)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // Display truncated version for long IDs
  const displayId = villageId.length > 12
    ? `${villageId.slice(0, 6)}...${villageId.slice(-4)}`
    : villageId

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-1 bg-slate-100 dark:bg-slate-700/50 rounded text-xs ${className}`}
      title={villageId}
    >
      <span className="font-mono text-slate-600 dark:text-slate-300">
        {displayId}
      </span>
      <button
        onClick={handleCopy}
        className="p-0.5 hover:bg-slate-200 dark:hover:bg-slate-600 rounded transition-colors"
        title="Copy Village ID"
      >
        {copied ? (
          <Check className="w-3 h-3 text-green-500" />
        ) : (
          <Copy className="w-3 h-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" />
        )}
      </button>
    </div>
  )
}
