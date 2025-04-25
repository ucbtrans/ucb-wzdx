// components/Navbar.js
import Link from 'next/link';

const Navbar = () => {
  return (
    <nav className="bg-orange-500 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-white font-bold text-lg">
          ZoneMapper
        </Link>
        <div className="space-x-4">
          <Link href="/about" className="text-white hover:underline">
            About
          </Link>
          <Link href="/services" className="text-white hover:underline">
            Services
          </Link>
          <Link href="/features" className="text-white hover:underline">
            Features
          </Link>
          <Link href="/contact" className="text-white hover:underline">
            Contact
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;