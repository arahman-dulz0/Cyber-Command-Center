import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Reveal } from "./reveal";

export function Section({
  id,
  eyebrow,
  title,
  intro,
  children,
  className,
}: {
  id?: string;
  eyebrow?: string;
  title?: ReactNode;
  intro?: string;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <section
      id={id}
      className={cn("relative mx-auto w-full max-w-7xl px-6 py-24 md:py-32", className)}
    >
      {(eyebrow || title || intro) && (
        <Reveal className="mb-14 max-w-2xl">
          {eyebrow && <div className="eyebrow mb-4">{eyebrow}</div>}
          {title && (
            <h2 className="font-display text-3xl font-semibold tracking-tight text-balance md:text-5xl">
              {title}
            </h2>
          )}
          {intro && (
            <p className="mt-5 text-lg leading-relaxed text-muted">{intro}</p>
          )}
        </Reveal>
      )}
      {children}
    </section>
  );
}
