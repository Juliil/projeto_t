const S = ({ children, ...p }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
       strokeLinecap="round" strokeLinejoin="round" {...p}>{children}</svg>
);

export const IcHome = (p) => (<S {...p}><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /></S>);
export const IcBox = (p) => (<S {...p}><path d="M21 8 12 3 3 8v8l9 5 9-5z" /><path d="M3 8l9 5 9-5M12 13v8" /></S>);
export const IcCalc = (p) => (<S {...p}><rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 7h8M8 11h2M8 15h2M14 11v6" /></S>);
export const IcStore = (p) => (<S {...p}><path d="M4 9h16l-1-5H5L4 9z" /><path d="M5 9v11h14V9M9 20v-6h6v6" /></S>);
export const IcLogout = (p) => (<S {...p}><path d="M15 4h4v16h-4" /><path d="M10 12h9M14 8l-4 4 4 4" /></S>);
export const IcBell = (p) => (<S {...p}><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M10 21h4" /></S>);
export const IcPlus = (p) => (<S {...p}><path d="M12 5v14M5 12h14" /></S>);
export const IcTrash = (p) => (<S {...p}><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" /></S>);
export const IcGavel = (p) => (<S {...p}><path d="M14 6 18 10M5 19l8-8M11 4l5 5-3 3-5-5zM3 21h7" /></S>);
export const IcChevron = (p) => (<S {...p}><path d="M15 6l-6 6 6 6" /></S>);
export const IcEdit = (p) => (<S {...p}><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" /></S>);
export const IcAlert = (p) => (<S {...p}><path d="M12 9v4M12 17h.01" /><path d="M10.3 3.9 2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" /></S>);
export const IcCalendar = (p) => (<S {...p}><rect x="3" y="4.5" width="18" height="16" rx="2" /><path d="M3 9h18M8 2.5v4M16 2.5v4" /></S>);
export const IcReceipt = (p) => (<S {...p}><path d="M5 3v18l2-1.2L9 21l2-1.2L13 21l2-1.2L17 21l2-1.2V3l-2 1.2L15 3l-2 1.2L11 3 9 4.2 7 3 5 4.2z" /><path d="M8 8h8M8 12h8M8 16h5" /></S>);
