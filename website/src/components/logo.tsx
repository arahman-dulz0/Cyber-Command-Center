export function Logo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="ccc-logo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#4c82fb" />
          <stop offset="0.5" stopColor="#34e4ea" />
          <stop offset="1" stopColor="#9b6cff" />
        </linearGradient>
      </defs>
      <path
        d="M16 2.2 27.5 7.8 V16.6 C27.5 23.5 22.4 28.6 16 30.8 9.6 28.6 4.5 23.5 4.5 16.6 V7.8 Z"
        stroke="url(#ccc-logo)"
        strokeWidth="1.5"
        strokeLinejoin="round"
        opacity="0.9"
      />
      <circle cx="16" cy="16" r="6.6" stroke="url(#ccc-logo)" strokeWidth="1" opacity="0.45" />
      <circle cx="16" cy="16" r="3.1" stroke="url(#ccc-logo)" strokeWidth="1.4" />
      <circle cx="16" cy="16" r="1.5" fill="#34e4ea" />
    </svg>
  );
}
