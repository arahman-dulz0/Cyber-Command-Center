import { ImageResponse } from "next/og";

export const dynamic = "force-static";
export const alt = "Cyber Command Center OSS — AI Cybersecurity Operations Platform";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background:
            "radial-gradient(1000px 500px at 80% -10%, rgba(76,130,251,0.35), transparent 60%), radial-gradient(900px 500px at -10% 110%, rgba(155,108,255,0.28), transparent 60%), #05070d",
          padding: "72px",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: "linear-gradient(135deg, #4c82fb, #9b6cff)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 30,
            }}
          >
            🛡️
          </div>
          <div
            style={{
              display: "flex",
              gap: 8,
              color: "#97a4b9",
              fontSize: 26,
              letterSpacing: 2,
            }}
          >
            <span>CYBER COMMAND CENTER</span>
            <span style={{ color: "#34e4ea" }}>· OSS</span>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: 72,
              fontWeight: 700,
              color: "#e8eef7",
              lineHeight: 1.05,
              letterSpacing: -1.5,
            }}
          >
            Autonomous threat intelligence.
          </div>
          <div
            style={{
              fontSize: 72,
              fontWeight: 700,
              lineHeight: 1.05,
              letterSpacing: -1.5,
              background: "linear-gradient(90deg, #4c82fb, #34e4ea 55%, #9b6cff)",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            Self-hosted cyber operations.
          </div>
        </div>

        <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
          {["AI Security Analyst", "Threat Fusion", "SOC Dashboard", "Self-hosted", "MIT"].map(
            (t) => (
              <div
                key={t}
                style={{
                  border: "1px solid #1b2436",
                  borderRadius: 10,
                  padding: "10px 18px",
                  color: "#97a4b9",
                  fontSize: 24,
                }}
              >
                {t}
              </div>
            )
          )}
        </div>
      </div>
    ),
    { ...size }
  );
}
