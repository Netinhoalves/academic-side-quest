import { useEffect } from 'react';

export default function Modal({ children, onClose, titleId }) {
    useEffect(() => {
        const scrollAnterior = window.scrollY;
        const bodyStyles = {
            position: document.body.style.position,
            top: document.body.style.top,
            left: document.body.style.left,
            right: document.body.style.right,
            width: document.body.style.width,
            overflow: document.body.style.overflow,
        };

        document.body.style.position = 'fixed';
        document.body.style.top = `-${scrollAnterior}px`;
        document.body.style.left = '0';
        document.body.style.right = '0';
        document.body.style.width = '100%';
        document.body.style.overflow = 'hidden';

        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.position = bodyStyles.position;
            document.body.style.top = bodyStyles.top;
            document.body.style.left = bodyStyles.left;
            document.body.style.right = bodyStyles.right;
            document.body.style.width = bodyStyles.width;
            document.body.style.overflow = bodyStyles.overflow;
            window.scrollTo(0, scrollAnterior);
        };
    }, [onClose]);

    const bloquearScrollDoFundo = (event) => {
        if (event.target === event.currentTarget) {
            event.preventDefault();
        }
    };

    return (
        <div
            className="fixed inset-0 z-[50] h-[100dvh] overflow-hidden bg-black/45 p-4 sm:p-5"
            style={{
                paddingTop: 'max(1rem, env(safe-area-inset-top))',
                paddingRight: 'max(1rem, env(safe-area-inset-right))',
                paddingBottom: 'max(1rem, env(safe-area-inset-bottom))',
                paddingLeft: 'max(1rem, env(safe-area-inset-left))',
                overscrollBehavior: 'none',
                touchAction: 'none',
            }}
            role="presentation"
            onTouchMove={bloquearScrollDoFundo}
        >
            <div className="flex h-full items-start justify-center sm:items-center">
                <div
                    className="relative w-full max-w-[560px] max-h-[calc(100dvh-2rem)] overflow-y-auto overflow-x-hidden overscroll-contain rounded-[15px] bg-color-yellow shadow-[0_18px_30px_rgba(0,0,0,0.3)]"
                    style={{
                        maxHeight: 'calc(100dvh - max(2rem, env(safe-area-inset-top) + env(safe-area-inset-bottom)))',
                        touchAction: 'pan-y',
                        WebkitOverflowScrolling: 'touch',
                    }}
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
