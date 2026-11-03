import { useEffect } from 'react';

export default function Modal({ children, onClose, titleId }) {
    useEffect(() => {
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [onClose]);

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/45 p-4" role="presentation">
            <div className="flex min-h-full items-start justify-center sm:items-center">
                <div
                    className="relative my-auto max-h-[calc(100dvh-2rem)] w-full max-w-[560px] overflow-visible rounded-[15px] bg-color-yellow shadow-[0_18px_30px_rgba(0,0,0,0.3)]"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby={titleId}
                >
                    {children}
                </div>
            </div>
        </div>
    );
}
