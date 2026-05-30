export default function TattooMachine({ className = "" }) {
  return (
    <svg
      className={`sketch ${className}`}
      viewBox="0 0 300 380"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g stroke="#f4f1ea" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        {/* Frame principal (corpo da máquina) */}
        <path d="M196 96
                 C232 100 244 130 240 168
                 C236 206 214 214 196 214
                 L150 214
                 C132 214 120 226 120 244
                 L120 260" />
        <path d="M118 96 L210 96
                 C214 96 218 100 218 104 L218 118" />
        {/* Base sob as bobinas */}
        <path d="M138 214 L228 214" />
        <path d="M150 214 L150 232 L226 232 L226 214" />

        {/* Bobinas (dois cilindros verticais) */}
        <g>
          <rect x="150" y="118" width="34" height="98" rx="6" />
          <line x1="150" y1="140" x2="184" y2="140" />
          <line x1="150" y1="158" x2="184" y2="158" />
          <line x1="150" y1="176" x2="184" y2="176" />
          <line x1="150" y1="194" x2="184" y2="194" />
        </g>
        <g>
          <rect x="192" y="118" width="34" height="98" rx="6" />
          <line x1="192" y1="140" x2="226" y2="140" />
          <line x1="192" y1="158" x2="226" y2="158" />
          <line x1="192" y1="176" x2="226" y2="176" />
          <line x1="192" y1="194" x2="226" y2="194" />
        </g>

        {/* Barra da armadura + mola */}
        <path d="M134 100 L240 100" />
        <path d="M150 100 L150 112 M208 100 L208 112" />
        <path d="M134 100 C120 100 116 90 124 84 L150 70" />

        {/* Cabo / tubo descendo até a ponta */}
        <path d="M120 244
                 C104 250 92 262 84 280
                 L58 332" />
        <path d="M138 244
                 C124 252 112 266 104 286
                 L78 338" />
        <line x1="58" y1="332" x2="78" y2="338" />

        {/* Grip (anel) */}
        <ellipse cx="103" cy="266" rx="11" ry="20" transform="rotate(-32 103 266)" />
      </g>

      {/* Parafuso de contato (acento) */}
      <g stroke="#d83a2b" strokeWidth="3" strokeLinecap="round">
        <line x1="150" y1="70" x2="150" y2="48" />
        <circle cx="150" cy="44" r="6" fill="#d83a2b" stroke="none" />
      </g>

      {/* Ponta / agulha */}
      <line x1="68" y1="335" x2="48" y2="356" stroke="#d83a2b" strokeWidth="3" strokeLinecap="round" />
      <circle cx="46" cy="358" r="3.4" fill="#d83a2b" />
    </svg>
  );
}
