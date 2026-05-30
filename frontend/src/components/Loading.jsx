import { useEffect, useState } from "react";

export default function Loading({ empresa = "Projeto T", onDone }) {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const t1 = setTimeout(() => setStage(1), 1550);
    const t2 = setTimeout(() => onDone && onDone(), 3000);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [onDone]);

  return (
    <div className="loading">
      <svg viewBox="0 0 240 90" xmlns="http://www.w3.org/2000/svg">
        <path
          className="ln"
          d="M20 60 C45 20 60 80 90 50 C115 26 130 70 160 48 C185 30 200 64 220 40"
        />
        <circle className="nib" cx="220" cy="40" r="5" />
      </svg>
      {stage === 0 ? (
        <div className="msg" key="a">estamos riscando…</div>
      ) : (
        <div className="msg welcome" key="b">Bem-vindo a {empresa}</div>
      )}
    </div>
  );
}
