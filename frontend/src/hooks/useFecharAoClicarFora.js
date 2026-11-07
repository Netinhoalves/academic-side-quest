import { useEffect, useRef } from 'react';

export function useFecharAoClicarFora(ref, aoFechar, ativo = true) {
    const callbackRef = useRef(aoFechar);

    useEffect(() => {
        callbackRef.current = aoFechar;
    }, [aoFechar]);

    useEffect(() => {
        if (!ativo) return;

        const handleInteracaoFora = (event) => {
            if (ref.current && !ref.current.contains(event.target)) {
                callbackRef.current();
            }
        };

        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                event.stopPropagation();
                callbackRef.current();
            }
        };

        document.addEventListener('mousedown', handleInteracaoFora, true);
        document.addEventListener('touchstart', handleInteracaoFora, true);
        document.addEventListener('keydown', handleKeyDown, true);

        return () => {
            document.removeEventListener('mousedown', handleInteracaoFora, true);
            document.removeEventListener('touchstart', handleInteracaoFora, true);
            document.removeEventListener('keydown', handleKeyDown, true);
        };
    }, [ref, ativo]);
}

export default useFecharAoClicarFora;