import logoAsq from '../assets/logo-sigla.png';

export default function Header({ nome}) {
    const iniciais = nome ? nome.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'US';

    return (
        <header className="bg-color-orange-bright h-[85px] w-full px-4 flex justify-between items-center">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-color-blue font-bold text-xl">
                    {iniciais}
                </div>
                <div className="text-white">
                    <p className="font-bold text-xl leading-tight">{nome}</p>
                </div>
            </div>
            <img src={logoAsq} alt="Logo ASQ" className='h-12 w-auto' />
        </header>
    );
}