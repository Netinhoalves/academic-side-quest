export function ActionButtons({src, alt, type = "button", onClick}) {
    return (
        <button type={type} onClick={onClick} className="hover:opacity-80 transition-opacity">
            <img src={src} alt={alt} className="w-[100px] h-[40px]" />
        </button>
    )
}
