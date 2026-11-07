import { useEffect } from "react";

export function useFecharAoClicarFora(ref, aoFechar, ativo = true) {
    useEffect(() => {
        if (!ativo) return;

        const handleInteracaoFora = (event) => {
            if(ref.current && !ref.current.contains(event.target)) {
                aoFechar();
            }
        };

        const handleKeyDown = (event) => {
            if(event.key === 'Escape') {
                aoFechar();
            }
        };

        document.addEventListener('mousedown', handleInteracaoFora);
        document.addEventListener('touchstart', handleInteracaoFora);
        document.addEventListener('keydown', handleKeyDown);

        return () => {
            document.removeEventListener('mousedown', handleInteracaoFora);
            document.removeEventListener('touchstart', handleInteracaoFora);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [ref, aoFechar, ativo]);
}

export default useFecharAoClicarFora;