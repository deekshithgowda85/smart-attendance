import React, { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Bell, User, ChevronDown, Menu, X } from "lucide-react";

const navLinks = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/attendance", label: "Attendance" },
  { to: "/students", label: "Students" },
  { to: "/analytics", label: "Analytics" },
  { to: "/reports", label: "Reports" },
  { to: "/manage-schedule", label: "Schedule" },
];

export default function Header({ theme, setTheme}) {
  const [user, setUser] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    try {
      const storedData = localStorage.getItem("user");
      if (!storedData) { setUser(null); return; }
      setUser(JSON.parse(storedData));
    } catch (e) {
      console.error("Failed to parse user from local storage", e);
      setUser(null);
    }
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  const displayName = user?.name || user?.email || "Guest";

  const isActive = (path) => location.pathname === path;

  return (
    <>
    <div className="w-full h-16 flex items-center justify-start px-6 bg-[var(--bg-card)] gap-2" role="navigation">
        <div className="logo-section flex items-center gap-4">
            <img className="w-14 h-14 rounded-full" src="logo.png" alt="" />
            <h1 className="text-2xl font-semibold text-[var(--text-main)]">Smart Attendance</h1>
        </div>
        <div className="nav-links text-gray-500 gap-1 ml-10">
            <a href="/" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">Dashboard</a>
            <a href="/attendance" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">Attendance</a>
            <a href="/students" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">Student</a>
            <a href="/analytics" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">Analytics</a>
            <a href="/reports" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">Reports</a>
            <a href="/manage-schedule" className="mx-2 font-semibold hover:text-[var(--primary)] hover:bg-[var(--primary-hover)] py-2 px-3 rounded-4xl">ManageSchedule</a>
        </div>

        {/* Center: Desktop nav links */}
        <nav className="hidden lg:flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
                isActive(link.to)
                  ? "text-[var(--primary)] bg-[var(--primary-hover)]/20"
                  : "text-[var(--text-body)] hover:text-[var(--primary)] hover:bg-[var(--bg-secondary)]"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right: Profile section */}
        <div className="flex items-center gap-3">
          <div className="bg-[var(--primary)] p-1.5 rounded-full cursor-pointer">
            <Bell size={16} className="text-[var(--text-on-primary)]" />
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <User size={20} className="text-[var(--text-body)]" />
            <span className="text-sm font-medium text-[var(--text-main)]">{displayName}</span>
            <Link to="/settings">
              <ChevronDown size={16} className="text-[var(--text-body)] cursor-pointer" />
            </Link>
          </div>
        </div>
      </div>

      {/* Mobile nav drawer */}
      {menuOpen && (
        <nav className="lg:hidden border-t border-[var(--border-color)] bg-[var(--bg-card)] px-4 pb-4 pt-2 space-y-1 animate-in slide-in-from-top">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`block px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                isActive(link.to)
                  ? "text-[var(--primary)] bg-[var(--primary-hover)]/20"
                  : "text-[var(--text-body)] hover:text-[var(--primary)] hover:bg-[var(--bg-secondary)]"
              }`}
            >
              {link.label}
            </Link>
          ))}
          {/* Mobile-only profile link */}
          <div className="sm:hidden flex items-center gap-2 px-4 py-2.5 border-t border-[var(--border-color)] mt-2 pt-3">
            <User size={18} className="text-[var(--text-body)]" />
            <span className="text-sm font-medium text-[var(--text-main)]">{displayName}</span>
          </div>
        </nav>
      )}
    </header>
  );
}
