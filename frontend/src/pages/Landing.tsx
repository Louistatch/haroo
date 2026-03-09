import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion, useScroll, useTransform, AnimatePresence, animate } from "framer-motion";
import { AnimatedSection, StaggerContainer, StaggerItem } from "../components/AnimatedSection";

/* ============================================================
   ICONS (SVG inline — pas d'emojis)
   ============================================================ */

function IconDocument() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
  );
}

function IconUsers() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  );
}

function IconTrendingUp() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
      <polyline points="17 6 23 6 23 12"/>
    </svg>
  );
}

function IconShield() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  );
}

function IconMapPin() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
      <circle cx="12" cy="10" r="3"/>
    </svg>
  );
}

function IconZap() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  );
}

function IconCheck() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  );
}

function IconArrowRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12"/>
      <polyline points="12 5 19 12 12 19"/>
    </svg>
  );
}

/* ============================================================
   COUNTER ANIMÉ
   ============================================================ */
function AnimatedCounter({ to, suffix = "", prefix = "" }: { to: number; suffix?: string; prefix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const [started, setStarted] = useState(false);
  const elemRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting && !started) setStarted(true); },
      { threshold: 0.5 }
    );
    if (elemRef.current) observer.observe(elemRef.current);
    return () => observer.disconnect();
  }, [started]);

  useEffect(() => {
    if (!started || !ref.current) return;
    const controls = animate(0, to, {
      duration: 1.8,
      ease: "easeOut",
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = prefix + Math.round(v).toLocaleString() + suffix;
      },
    });
    return () => controls.stop();
  }, [started, to, suffix, prefix]);

  return (
    <div ref={elemRef}>
      <span ref={ref}>{prefix}0{suffix}</span>
    </div>
  );
}

/* ============================================================
   DATA
   ============================================================ */
const services = [
  {
    icon: <IconDocument />,
    title: "Documents Techniques",
    desc: "Itinéraires culturaux, comptes d'exploitation prévisionnels — adaptés à votre région et vos cultures.",
    cta: "Explorer le catalogue",
    to: "/documents",
    color: "#16a34a",
  },
  {
    icon: <IconUsers />,
    title: "Annuaire des Agronomes",
    desc: "Trouvez et contactez des agronomes certifiés dans votre canton pour accompagner vos projets.",
    cta: "Voir les agronomes",
    to: "/agronomists",
    color: "#0ea5e9",
  },
  {
    icon: <IconTrendingUp />,
    title: "Analyses de Marché",
    desc: "Prévisions de prix, analyses de la demande et recommandations de marchés optimaux pour vos cultures.",
    cta: "Accéder aux analyses",
    to: "/markets",
    color: "#8b5cf6",
  },
  {
    icon: <IconUsers />,
    title: "Recrutement Agricole",
    desc: "Recrutez des ouvriers qualifiés et des experts agronomes pour vos missions et travaux saisonniers.",
    cta: "Recruter maintenant",
    to: "/jobs",
    color: "#f59e0b",
  },
  {
    icon: <IconZap />,
    title: "Préventes Agricoles",
    desc: "Sécurisez vos revenus avec un système de préventes et d'acomptes garanti par la plateforme.",
    cta: "Créer une prévente",
    to: "/presales",
    color: "#ec4899",
  },
  {
    icon: <IconMapPin />,
    title: "Logistique & Transport",
    desc: "Optimisez vos itinéraires et trouvez des transporteurs vérifiés au meilleur prix dans votre région.",
    cta: "Optimiser mes trajets",
    to: "/register",
    color: "#06b6d4",
  },
];

const features = [
  { icon: <IconShield />, title: "Sécurisé", desc: "Paiements chiffrés via Fedapay. Vos données protégées selon les standards internationaux.", color: "#16a34a" },
  { icon: <IconMapPin />, title: "Géolocalisé", desc: "Services adaptés à votre région, préfecture et canton. Contenu 100% pertinent pour vous.", color: "#0ea5e9" },
  { icon: <IconZap />, title: "Instantané", desc: "Accès immédiat après paiement. Téléchargez vos documents et contactez des experts en secondes.", color: "#8b5cf6" },
  { icon: <IconUsers />, title: "Vérifié", desc: "Chaque agronome est identifié et certifié. Chaque document est validé par des experts du terrain.", color: "#f59e0b" },
];

const steps = [
  { step: "01", title: "Créez votre compte", desc: "Inscrivez-vous avec votre numéro togolais (+228) en 2 minutes. Aucun email requis.", detail: "Simple · Rapide · Gratuit" },
  { step: "02", title: "Parcourez les services", desc: "Documents, agronomes, analyses de marché — tout est accessible depuis votre tableau de bord.", detail: "5 Régions · 40+ Cantons" },
  { step: "03", title: "Payez via Mobile Money", desc: "Flooz ou T-Money. Accès instantané à vos ressources après confirmation.", detail: "Sécurisé · Instantané" },
];

const testimonials = [
  {
    quote: "J'ai pu doubler mon rendement en maïs grâce au guide technique Haroo. Tout y est : dosage d'engrais, calendrier cultural, gestion des ravageurs.",
    name: "Kofi Mensah",
    role: "Producteur de maïs",
    region: "Région des Plateaux",
    initials: "KM",
    color: "#16a34a",
    photo: "/images/users/agronomist-1.jpg",
  },
  {
    quote: "Haroo m'a permis de trouver un agronome certifié dans ma préfecture en moins d'une heure. Le service est impressionnant.",
    name: "Akosua Lawson",
    role: "Exploitante agricole",
    region: "Région de la Kara",
    initials: "AL",
    color: "#0ea5e9",
    photo: "/images/users/agronomist-5.jpg",
  },
  {
    quote: "Les analyses de marché m'ont aidé à choisir le bon moment pour vendre mes ignames. J'ai gagné 30% de plus cette saison.",
    name: "Yao Dossou",
    role: "Agriculteur",
    region: "Région des Savanes",
    initials: "YD",
    color: "#8b5cf6",
    photo: "/images/users/agronomist-9.jpg",
  },
];

/* ============================================================
   HERO BACKGROUND PARTICLES
   ============================================================ */
function HeroBackground() {
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
      {/* Grid pattern */}
      <div style={{
        position: "absolute",
        inset: 0,
        backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
        backgroundSize: "60px 60px",
      }} />
      {/* Radial glow */}
      <div style={{
        position: "absolute",
        top: "20%",
        left: "50%",
        transform: "translateX(-50%)",
        width: "800px",
        height: "600px",
        background: "radial-gradient(ellipse, rgba(34,197,94,0.15) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />
      {/* Floating orbs */}
      {[
        { size: 300, top: "10%", left: "5%", color: "rgba(22,163,74,0.08)", duration: 8 },
        { size: 200, top: "60%", right: "8%", color: "rgba(14,165,233,0.08)", duration: 11 },
        { size: 150, top: "80%", left: "15%", color: "rgba(139,92,246,0.06)", duration: 9 },
      ].map((orb, i) => (
        <motion.div
          key={i}
          animate={{ y: [-20, 20, -20], x: [-10, 10, -10] }}
          transition={{ duration: orb.duration, repeat: Infinity, ease: "easeInOut" }}
          style={{
            position: "absolute",
            width: orb.size,
            height: orb.size,
            borderRadius: "50%",
            background: orb.color,
            filter: "blur(60px)",
            top: orb.top,
            left: (orb as any).left,
            right: (orb as any).right,
          }}
        />
      ))}
    </div>
  );
}

/* ============================================================
   MAIN COMPONENT
   ============================================================ */
export default function Landing() {
  const navigate = useNavigate();
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 80]);

  const words = ["agriculteurs", "coopératives", "agronomes", "exploitants"];
  const [wordIndex, setWordIndex] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setWordIndex((i) => (i + 1) % words.length), 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ background: "var(--bg)", minHeight: "100vh" }}>

      {/* ====== HERO ====== */}
      <section
        ref={heroRef}
        style={{
          position: "relative",
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          background: "linear-gradient(135deg, #052e16 0%, #14532d 40%, #15803d 100%)",
          overflow: "hidden",
          paddingTop: "64px",
        }}
      >
        {/* Image de fond réelle */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: "url('/images/hero/agriculture.jpg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          opacity: 0.2,
        }} />
        <div style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(135deg, rgba(5,46,22,0.85) 0%, rgba(20,83,45,0.8) 40%, rgba(21,128,61,0.75) 100%)",
        }} />
        <HeroBackground />

        <motion.div
          className="container"
          style={{ opacity: heroOpacity, y: heroY, position: "relative", zIndex: 1 }}
        >
          <div style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center", padding: "4rem 0 6rem" }}>
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              style={{ marginBottom: "2rem" }}
            >
              <span style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                background: "rgba(34,197,94,0.15)",
                border: "1px solid rgba(34,197,94,0.3)",
                borderRadius: "100px",
                padding: "6px 16px",
                fontSize: "0.8rem",
                fontWeight: 600,
                color: "#86efac",
                letterSpacing: "0.04em",
                textTransform: "uppercase",
              }}>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
                Plateforme #1 au Togo
              </span>
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.1 }}
              style={{
                fontSize: "clamp(2.5rem, 6vw, 4.5rem)",
                fontWeight: 900,
                color: "white",
                lineHeight: 1.1,
                letterSpacing: "-0.04em",
                marginBottom: "1.5rem",
              }}
            >
              L'agriculture togolaise<br />
              entre dans{" "}
              <span style={{
                background: "linear-gradient(90deg, #4ade80, #22c55e)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}>
                l'ère digitale
              </span>
            </motion.h1>

            {/* Animated subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              style={{
                fontSize: "clamp(1.1rem, 2.5vw, 1.35rem)",
                color: "rgba(255,255,255,0.75)",
                lineHeight: 1.7,
                marginBottom: "1rem",
              }}
            >
              La première plateforme conçue pour les{" "}
              <span style={{ display: "inline-block", overflow: "hidden", height: "1.4em", verticalAlign: "text-bottom" }}>
                <AnimatePresence mode="wait">
                  <motion.span
                    key={wordIndex}
                    initial={{ y: "100%" }}
                    animate={{ y: "0%" }}
                    exit={{ y: "-100%" }}
                    transition={{ duration: 0.4, ease: [0.0, 0, 0.2, 1] }}
                    style={{ display: "inline-block", color: "#4ade80", fontWeight: 700 }}
                  >
                    {words[wordIndex]}
                  </motion.span>
                </AnimatePresence>
              </span>{" "}
              togolais.
            </motion.p>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.3 }}
              style={{
                fontSize: "1rem",
                color: "rgba(255,255,255,0.55)",
                marginBottom: "2.5rem",
              }}
            >
              Documents techniques · Agronomes certifiés · Analyses de marché · Mobile Money
            </motion.p>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}
            >
              <motion.button
                whileHover={{ scale: 1.03, boxShadow: "0 20px 40px rgba(34,197,94,0.35)" }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate("/register")}
                style={{
                  background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  color: "white",
                  border: "none",
                  padding: "16px 32px",
                  borderRadius: "14px",
                  fontSize: "1.05rem",
                  fontWeight: 700,
                  cursor: "pointer",
                  boxShadow: "0 8px 24px rgba(22,163,74,0.4)",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  letterSpacing: "-0.01em",
                }}
              >
                Commencer gratuitement
                <IconArrowRight />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02, background: "rgba(255,255,255,0.15)" }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate("/documents")}
                style={{
                  background: "rgba(255,255,255,0.08)",
                  color: "white",
                  border: "1px solid rgba(255,255,255,0.2)",
                  padding: "16px 32px",
                  borderRadius: "14px",
                  fontSize: "1.05rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  backdropFilter: "blur(8px)",
                }}
              >
                Voir les documents
              </motion.button>
            </motion.div>

            {/* Trust badges */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              style={{
                marginTop: "3rem",
                display: "flex",
                gap: "2rem",
                justifyContent: "center",
                flexWrap: "wrap",
              }}
            >
              {["Paiement Mobile Money", "Accès instantané", "100% Togolais"].map((t) => (
                <span key={t} style={{ display: "flex", alignItems: "center", gap: "6px", color: "rgba(255,255,255,0.6)", fontSize: "0.85rem" }}>
                  <span style={{ color: "#4ade80", display: "flex" }}><IconCheck /></span>
                  {t}
                </span>
              ))}
            </motion.div>
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          style={{ position: "absolute", bottom: "2rem", left: "50%", transform: "translateX(-50%)", zIndex: 1 }}
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
            style={{ width: "24px", height: "40px", border: "2px solid rgba(255,255,255,0.25)", borderRadius: "12px", display: "flex", justifyContent: "center", paddingTop: "6px" }}
          >
            <div style={{ width: "4px", height: "8px", borderRadius: "2px", background: "rgba(255,255,255,0.5)" }} />
          </motion.div>
        </motion.div>
      </section>

      {/* ====== STATS ====== */}
      <section style={{ background: "var(--surface)", borderBottom: "1px solid var(--border)" }}>
        <div className="container">
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: "0",
            padding: "0",
          }}>
            {[
              { value: 5, suffix: "", label: "Régions couvertes", color: "#16a34a" },
              { value: 39, suffix: "+", label: "Préfectures", color: "#0ea5e9" },
              { value: 300, suffix: "+", label: "Cantons", color: "#8b5cf6" },
              { value: 12, suffix: "", label: "Documents disponibles", color: "#f59e0b" },
            ].map((stat, i) => (
              <AnimatedSection key={stat.label} delay={i * 0.08} direction="up">
                <div style={{
                  padding: "2.5rem 2rem",
                  textAlign: "center",
                  borderRight: i < 3 ? "1px solid var(--border)" : "none",
                  position: "relative",
                }}>
                  <div style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)", fontWeight: 900, color: stat.color, letterSpacing: "-0.04em", lineHeight: 1 }}>
                    <AnimatedCounter to={stat.value} suffix={stat.suffix} />
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.5rem", fontWeight: 500 }}>
                    {stat.label}
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* ====== CULTURES GALLERY ====== */}
      <section style={{ padding: "5rem 0", background: "var(--bg)", overflow: "hidden" }}>
        <div className="container">
          <AnimatedSection style={{ textAlign: "center", marginBottom: "2.5rem" }}>
            <span style={{
              display: "inline-block", padding: "4px 14px", borderRadius: "100px",
              background: "var(--primary-glow)", color: "var(--primary)",
              fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em",
              textTransform: "uppercase", marginBottom: "1rem",
            }}>
              Cultures du Togo
            </span>
            <h2 style={{ fontSize: "clamp(1.6rem, 3vw, 2.2rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
              Des ressources pour chaque filière
            </h2>
          </AnimatedSection>

          <StaggerContainer
            style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "1rem" }}
            staggerDelay={0.06}
          >
            {[
              { name: "Maïs", img: "/images/cultures/mais.jpg", color: "#f59e0b" },
              { name: "Riz", img: "/images/cultures/riz.jpg", color: "#16a34a" },
              { name: "Soja", img: "/images/cultures/soja.jpg", color: "#84cc16" },
              { name: "Tomate", img: "/images/cultures/tomate.jpg", color: "#ef4444" },
              { name: "Manioc", img: "/images/cultures/manioc.jpg", color: "#8b5cf6" },
              { name: "Arachide", img: "/images/cultures/arachide.jpg", color: "#d97706" },
              { name: "Coton", img: "/images/cultures/coton.jpg", color: "#06b6d4" },
              { name: "Oignon", img: "/images/cultures/oignon.jpg", color: "#ec4899" },
            ].map((c) => (
              <StaggerItem key={c.name}>
                <motion.div
                  whileHover={{ y: -6, boxShadow: "0 12px 32px rgba(0,0,0,0.15)" }}
                  style={{
                    borderRadius: "16px",
                    overflow: "hidden",
                    border: "1px solid var(--border)",
                    background: "var(--surface)",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ position: "relative", paddingTop: "100%", overflow: "hidden" }}>
                    <img
                      src={c.img}
                      alt={c.name}
                      loading="lazy"
                      style={{
                        position: "absolute",
                        inset: 0,
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        transition: "transform 0.3s ease",
                      }}
                      onMouseOver={(e) => (e.currentTarget.style.transform = "scale(1.08)")}
                      onMouseOut={(e) => (e.currentTarget.style.transform = "scale(1)")}
                    />
                    <div style={{
                      position: "absolute",
                      bottom: 0,
                      left: 0,
                      right: 0,
                      background: "linear-gradient(transparent, rgba(0,0,0,0.7))",
                      padding: "2rem 0.75rem 0.75rem",
                    }}>
                      <span style={{
                        color: "white",
                        fontWeight: 700,
                        fontSize: "0.9rem",
                        textShadow: "0 1px 3px rgba(0,0,0,0.5)",
                      }}>
                        {c.name}
                      </span>
                    </div>
                  </div>
                </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ====== SERVICES ====== */}
      <section style={{ padding: "7rem 0", background: "var(--bg)" }}>
        <div className="container">
          <AnimatedSection style={{ textAlign: "center", marginBottom: "4rem" }}>
            <span style={{
              display: "inline-block",
              padding: "4px 14px",
              borderRadius: "100px",
              background: "var(--primary-glow)",
              color: "var(--primary)",
              fontSize: "0.75rem",
              fontWeight: 700,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              marginBottom: "1rem",
            }}>
              Services
            </span>
            <h2 style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1rem" }}>
              Tout ce dont vous avez besoin,<br />en un seul endroit
            </h2>
            <p style={{ fontSize: "1.1rem", color: "var(--text-secondary)", maxWidth: "560px", margin: "0 auto", lineHeight: 1.7 }}>
              Des outils numériques conçus spécifiquement pour le contexte agricole togolais.
            </p>
          </AnimatedSection>

          <StaggerContainer
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "1.25rem",
            }}
            staggerDelay={0.08}
          >
            {services.map((svc) => (
              <StaggerItem key={svc.title}>
                <motion.div
                  whileHover={{ y: -4, boxShadow: "var(--shadow-xl)" }}
                  transition={{ duration: 0.2 }}
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    borderRadius: "20px",
                    padding: "2rem",
                    display: "flex",
                    flexDirection: "column",
                    gap: "1rem",
                    cursor: "pointer",
                    boxShadow: "var(--shadow-sm)",
                    transition: "border-color 0.2s ease",
                  }}
                  onHoverStart={(e) => {
                    (e.target as HTMLElement).style.borderColor = svc.color + "40";
                  }}
                  onHoverEnd={(e) => {
                    (e.target as HTMLElement).style.borderColor = "var(--border)";
                  }}
                >
                  <div style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "14px",
                    background: svc.color + "15",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: svc.color,
                  }}>
                    {svc.icon}
                  </div>
                  <div>
                    <h3 style={{ fontWeight: 700, fontSize: "1.1rem", color: "var(--text)", marginBottom: "0.4rem", letterSpacing: "-0.02em" }}>
                      {svc.title}
                    </h3>
                    <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.6, margin: 0 }}>
                      {svc.desc}
                    </p>
                  </div>
                  <Link
                    to={svc.to}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "6px",
                      color: svc.color,
                      fontWeight: 600,
                      fontSize: "0.875rem",
                      marginTop: "auto",
                      paddingTop: "0.5rem",
                      borderTop: "1px solid var(--border)",
                      textDecoration: "none",
                    }}
                  >
                    {svc.cta}
                    <motion.span whileHover={{ x: 4 }} style={{ display: "flex" }}>
                      <IconArrowRight />
                    </motion.span>
                  </Link>
                </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ====== CARTE DES MARCHÉS ====== */}
      <section style={{ padding: "7rem 0", background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
        <div className="container">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center" }} className="markets-grid">
            <AnimatedSection direction="left">
              <span style={{
                display: "inline-block", padding: "4px 14px", borderRadius: "100px",
                background: "rgba(14,165,233,0.12)", color: "#0ea5e9",
                fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em",
                textTransform: "uppercase", marginBottom: "1.25rem",
              }}>
                Géolocalisation
              </span>
              <h2 style={{ fontSize: "clamp(1.8rem, 3.5vw, 2.5rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1.25rem", lineHeight: 1.2 }}>
                Marchés de proximité<br />
                <span style={{ color: "#0ea5e9" }}>à portée de main</span>
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "1rem", lineHeight: 1.8, marginBottom: "2rem" }}>
                Localisez les marchés agricoles les plus proches de votre exploitation. Comparez les prix, planifiez vos ventes et optimisez vos déplacements grâce à notre carte interactive.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "2rem" }}>
                {["Plus de 200 marchés référencés au Togo", "Filtrage par région et type de produit", "Itinéraires optimisés pour vos livraisons"].map((item) => (
                  <div key={item} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{ width: "22px", height: "22px", borderRadius: "50%", background: "rgba(14,165,233,0.12)", color: "#0ea5e9", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <IconCheck />
                    </span>
                    <span style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>{item}</span>
                  </div>
                ))}
              </div>
              <motion.button
                whileHover={{ scale: 1.03, boxShadow: "0 12px 28px rgba(14,165,233,0.3)" }}
                whileTap={{ scale: 0.97 }}
                onClick={() => navigate("/markets")}
                style={{
                  background: "linear-gradient(135deg, #0ea5e9, #0284c7)",
                  color: "white", border: "none", padding: "14px 28px",
                  borderRadius: "14px", fontSize: "1rem", fontWeight: 700,
                  cursor: "pointer", boxShadow: "0 6px 20px rgba(14,165,233,0.3)",
                  display: "inline-flex", alignItems: "center", gap: "8px",
                }}
              >
                <IconMapPin /> Explorer la carte
              </motion.button>
            </AnimatedSection>

            <AnimatedSection direction="right">
              <motion.div
                whileHover={{ scale: 1.01 }}
                style={{
                  borderRadius: "20px", overflow: "hidden",
                  boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
                  border: "1px solid var(--border)",
                  position: "relative",
                }}
              >
                <img
                  src="/images/hero/market.jpg"
                  alt="Marché agricole au Togo"
                  style={{ width: "100%", height: "380px", objectFit: "cover", display: "block" }}
                />
                <div style={{
                  position: "absolute", bottom: 0, left: 0, right: 0,
                  background: "linear-gradient(transparent, rgba(0,0,0,0.75))",
                  padding: "3rem 1.5rem 1.5rem",
                }}>
                  <div style={{ display: "flex", gap: "1.5rem" }}>
                    {[["200+", "Marchés"], ["5", "Régions"], ["Temps réel", "Données"]].map(([v, l]) => (
                      <div key={l}>
                        <div style={{ color: "#67e8f9", fontWeight: 800, fontSize: "1.2rem" }}>{v}</div>
                        <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.75rem", fontWeight: 500 }}>{l}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </AnimatedSection>
          </div>
        </div>
        <style>{`@media (max-width: 768px) { .markets-grid { grid-template-columns: 1fr !important; gap: 2rem !important; } }`}</style>
      </section>

      {/* ====== DEVENIR TECHNICIEN ====== */}
      <section style={{
        padding: "7rem 0",
        background: "linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)",
        position: "relative", overflow: "hidden",
      }}>
        <div style={{ position: "absolute", inset: 0, backgroundImage: "url('/images/hero/farmer.jpg')", backgroundSize: "cover", backgroundPosition: "center", opacity: 0.08 }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        <div style={{ position: "absolute", top: "20%", left: "50%", transform: "translateX(-50%)", width: "700px", height: "500px", background: "radial-gradient(ellipse, rgba(139,92,246,0.15) 0%, transparent 70%)", pointerEvents: "none" }} />

        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <AnimatedSection style={{ textAlign: "center", marginBottom: "4rem" }}>
            <span style={{
              display: "inline-block", padding: "6px 16px", borderRadius: "100px",
              background: "rgba(167,139,250,0.15)", border: "1px solid rgba(167,139,250,0.3)",
              color: "#c4b5fd", fontSize: "0.8rem", fontWeight: 600,
              letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "1.5rem",
            }}>
              Opportunité
            </span>
            <h2 style={{ fontSize: "clamp(2rem, 4vw, 3rem)", fontWeight: 900, color: "white", letterSpacing: "-0.04em", marginBottom: "1.25rem", lineHeight: 1.15 }}>
              Devenez Technicien<br />
              <span style={{ color: "#a78bfa" }}>de la Plateforme</span>
            </h2>
            <p style={{ fontSize: "1.1rem", color: "rgba(255,255,255,0.65)", maxWidth: "600px", margin: "0 auto", lineHeight: 1.7 }}>
              Vous êtes agronome ? Rejoignez notre réseau de techniciens certifiés. Partagez votre expertise, publiez des documents techniques et accompagnez les agriculteurs de votre localité.
            </p>
          </AnimatedSection>

          <StaggerContainer
            style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.5rem", maxWidth: "900px", margin: "0 auto 3rem" }}
            staggerDelay={0.1}
          >
            {[
              {
                step: "01",
                title: "Inscrivez-vous",
                desc: "Créez votre compte gratuitement et complétez votre profil agronome avec vos diplômes et spécialisations.",
                icon: <IconUsers />,
              },
              {
                step: "02",
                title: "Demandez le statut Technicien",
                desc: "Soumettez votre candidature avec vos justificatifs. Notre équipe valide votre profil sous 48h.",
                icon: <IconShield />,
              },
              {
                step: "03",
                title: "Publiez & Accompagnez",
                desc: "Uploadez des documents techniques par localité, devenez visible dans l'annuaire et recevez des missions.",
                icon: <IconDocument />,
              },
            ].map((s) => (
              <StaggerItem key={s.step}>
                <motion.div
                  whileHover={{ y: -6, boxShadow: "0 20px 50px rgba(0,0,0,0.3)" }}
                  style={{
                    background: "rgba(255,255,255,0.06)",
                    backdropFilter: "blur(12px)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "20px",
                    padding: "2rem",
                    textAlign: "center",
                  }}
                >
                  <div style={{
                    width: "52px", height: "52px", borderRadius: "14px",
                    background: "rgba(167,139,250,0.15)", border: "1px solid rgba(167,139,250,0.25)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    color: "#a78bfa", margin: "0 auto 1.25rem",
                  }}>
                    {s.icon}
                  </div>
                  <div style={{
                    display: "inline-block", padding: "2px 10px", borderRadius: "100px",
                    background: "rgba(167,139,250,0.12)", color: "#c4b5fd",
                    fontSize: "0.7rem", fontWeight: 700, letterSpacing: "0.06em",
                    marginBottom: "0.75rem",
                  }}>
                    ÉTAPE {s.step}
                  </div>
                  <h3 style={{ color: "white", fontWeight: 700, fontSize: "1.1rem", marginBottom: "0.6rem" }}>
                    {s.title}
                  </h3>
                  <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.88rem", lineHeight: 1.6, margin: 0 }}>
                    {s.desc}
                  </p>
                </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>

          <AnimatedSection style={{ textAlign: "center" }}>
            <div style={{ display: "flex", gap: "1.5rem", justifyContent: "center", flexWrap: "wrap", marginBottom: "2rem" }}>
              {[
                { value: "Gratuit", label: "Inscription" },
                { value: "48h", label: "Validation" },
                { value: "100%", label: "Visibilité" },
                { value: "∞", label: "Documents" },
              ].map((s) => (
                <div key={s.label} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "#a78bfa" }}>{s.value}</div>
                  <div style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.4)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</div>
                </div>
              ))}
            </div>
            <motion.button
              whileHover={{ scale: 1.03, boxShadow: "0 16px 40px rgba(139,92,246,0.4)" }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate("/register")}
              style={{
                background: "linear-gradient(135deg, #8b5cf6, #6d28d9)",
                color: "white", border: "none", padding: "16px 36px",
                borderRadius: "14px", fontSize: "1.05rem", fontWeight: 700,
                cursor: "pointer", boxShadow: "0 8px 24px rgba(139,92,246,0.35)",
                display: "inline-flex", alignItems: "center", gap: "8px",
              }}
            >
              Devenir Technicien <IconArrowRight />
            </motion.button>
          </AnimatedSection>
        </div>
      </section>

      {/* ====== RECHERCHE D'OUVRIERS ====== */}
      <section style={{ padding: "7rem 0", background: "var(--bg)" }}>
        <div className="container">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center" }} className="workers-grid">
            <AnimatedSection direction="right" style={{ order: 2 }}>
              <span style={{
                display: "inline-block", padding: "4px 14px", borderRadius: "100px",
                background: "rgba(245,158,11,0.12)", color: "#f59e0b",
                fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em",
                textTransform: "uppercase", marginBottom: "1.25rem",
              }}>
                Emploi Agricole
              </span>
              <h2 style={{ fontSize: "clamp(1.8rem, 3.5vw, 2.5rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1.25rem", lineHeight: 1.2 }}>
                Recrutez des ouvriers<br />
                <span style={{ color: "#f59e0b" }}>qualifiés</span>
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "1rem", lineHeight: 1.8, marginBottom: "1.5rem" }}>
                Publiez vos offres d'emploi saisonnier et trouvez la main-d'œuvre dont vous avez besoin. Les ouvriers inscrits sur la plateforme peuvent voir vos offres et vous contacter directement.
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "2rem" }}>
                {[
                  { icon: "📋", title: "Publiez une offre", desc: "Décrivez le poste, le salaire et la durée" },
                  { icon: "👁️", title: "Visibilité totale", desc: "Tous les ouvriers voient votre annonce" },
                  { icon: "📞", title: "Contact direct", desc: "Les ouvriers vous contactent directement" },
                  { icon: "✅", title: "Contrats sécurisés", desc: "Suivi et gestion via la plateforme" },
                ].map((item) => (
                  <div key={item.title} style={{
                    background: "var(--surface)", border: "1px solid var(--border)",
                    borderRadius: "14px", padding: "1rem",
                  }}>
                    <div style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{item.icon}</div>
                    <div style={{ fontWeight: 700, fontSize: "0.88rem", color: "var(--text)", marginBottom: "0.25rem" }}>{item.title}</div>
                    <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", lineHeight: 1.4 }}>{item.desc}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
                <motion.button
                  whileHover={{ scale: 1.03, boxShadow: "0 12px 28px rgba(245,158,11,0.3)" }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => navigate("/jobs")}
                  style={{
                    background: "linear-gradient(135deg, #f59e0b, #d97706)",
                    color: "white", border: "none", padding: "14px 28px",
                    borderRadius: "14px", fontSize: "1rem", fontWeight: 700,
                    cursor: "pointer", boxShadow: "0 6px 20px rgba(245,158,11,0.3)",
                    display: "inline-flex", alignItems: "center", gap: "8px",
                  }}
                >
                  Publier une offre <IconArrowRight />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02, background: "var(--surface)" }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => navigate("/jobs")}
                  style={{
                    background: "transparent", color: "#f59e0b",
                    border: "1.5px solid rgba(245,158,11,0.3)",
                    padding: "14px 28px", borderRadius: "14px",
                    fontSize: "1rem", fontWeight: 600, cursor: "pointer",
                  }}
                >
                  Voir les offres
                </motion.button>
              </div>
            </AnimatedSection>

            <AnimatedSection direction="left" style={{ order: 1 }}>
              <motion.div
                whileHover={{ scale: 1.01 }}
                style={{
                  borderRadius: "20px", overflow: "hidden",
                  boxShadow: "0 20px 60px rgba(0,0,0,0.12)",
                  border: "1px solid var(--border)",
                  position: "relative",
                }}
              >
                <img
                  src="/images/hero/harvest.jpg"
                  alt="Ouvriers agricoles au travail"
                  style={{ width: "100%", height: "420px", objectFit: "cover", display: "block" }}
                />
                <div style={{
                  position: "absolute", bottom: 0, left: 0, right: 0,
                  background: "linear-gradient(transparent, rgba(0,0,0,0.8))",
                  padding: "3rem 1.5rem 1.5rem",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
                    <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#4ade80", animation: "pulse-soft 2s ease-in-out infinite" }} />
                    <span style={{ color: "#86efac", fontSize: "0.8rem", fontWeight: 600 }}>Offres actives en ce moment</span>
                  </div>
                  <div style={{ display: "flex", gap: "1.5rem" }}>
                    {[["Récolte", "Semis", "Désherbage"], ["Irrigation", "Taille", "Entretien"]].flat().slice(0, 4).map((type) => (
                      <span key={type} style={{
                        background: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.15)",
                        borderRadius: "100px", padding: "4px 12px",
                        color: "rgba(255,255,255,0.8)", fontSize: "0.75rem", fontWeight: 600,
                      }}>
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            </AnimatedSection>
          </div>
        </div>
        <style>{`@media (max-width: 768px) { .workers-grid { grid-template-columns: 1fr !important; gap: 2rem !important; } .workers-grid > *:first-child { order: 2 !important; } .workers-grid > *:last-child { order: 1 !important; } }`}</style>
      </section>

      {/* ====== WHY US (Features) ====== */}
      <section style={{ padding: "7rem 0", background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
        <div className="container">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "5rem", alignItems: "center" }}>
            {/* Left: text */}
            <AnimatedSection direction="left">
              <span style={{
                display: "inline-block",
                padding: "4px 14px",
                borderRadius: "100px",
                background: "var(--primary-glow)",
                color: "var(--primary)",
                fontSize: "0.75rem",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                marginBottom: "1.25rem",
              }}>
                Pourquoi Haroo ?
              </span>
              <h2 style={{ fontSize: "clamp(1.8rem, 3.5vw, 2.5rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1.25rem", lineHeight: 1.2 }}>
                Conçu pour les réalités du terrain togolais
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "1rem", lineHeight: 1.8, marginBottom: "2rem" }}>
                Nous avons travaillé avec des agriculteurs, des agronomes et des institutions agricoles pour créer une plateforme qui répond vraiment aux besoins du terrain.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {["Contenus validés par des agronomes certifiés", "Paiement Mobile Money (Flooz, T-Money)", "Interface pensée pour mobile", "Support en langues locales à venir"].map((item) => (
                  <div key={item} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{ width: "22px", height: "22px", borderRadius: "50%", background: "var(--primary-glow)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <IconCheck />
                    </span>
                    <span style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>{item}</span>
                  </div>
                ))}
              </div>
            </AnimatedSection>

            {/* Right: feature cards */}
            <StaggerContainer style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }} staggerDelay={0.1}>
              {/* Image réelle */}
              <StaggerItem>
                <motion.div
                  whileHover={{ scale: 1.01 }}
                  style={{
                    borderRadius: "20px",
                    overflow: "hidden",
                    boxShadow: "0 16px 48px rgba(0,0,0,0.12)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <img
                    src="/images/hero/farmer.jpg"
                    alt="Agriculteur togolais dans son champ"
                    style={{ width: "100%", height: "240px", objectFit: "cover", display: "block" }}
                  />
                </motion.div>
              </StaggerItem>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              {features.map((f) => (
                <StaggerItem key={f.title}>
                  <motion.div
                    whileHover={{ scale: 1.02, boxShadow: "var(--shadow-lg)" }}
                    style={{
                      background: "var(--bg)",
                      border: "1px solid var(--border)",
                      borderRadius: "16px",
                      padding: "1.5rem",
                      boxShadow: "var(--shadow-sm)",
                    }}
                  >
                    <div style={{ width: "40px", height: "40px", borderRadius: "10px", background: f.color + "15", display: "flex", alignItems: "center", justifyContent: "center", color: f.color, marginBottom: "0.75rem" }}>
                      {f.icon}
                    </div>
                    <h4 style={{ fontWeight: 700, fontSize: "0.95rem", color: "var(--text)", marginBottom: "0.4rem" }}>{f.title}</h4>
                    <p style={{ color: "var(--text-secondary)", fontSize: "0.8rem", lineHeight: 1.5, margin: 0 }}>{f.desc}</p>
                  </motion.div>
                </StaggerItem>
              ))}
              </div>
            </StaggerContainer>
          </div>
        </div>

        {/* Mobile: stack the two columns */}
        <style>{`
          @media (max-width: 768px) {
            .why-grid { grid-template-columns: 1fr !important; }
          }
        `}</style>
      </section>

      {/* ====== HOW IT WORKS ====== */}
      <section style={{ padding: "7rem 0", background: "var(--bg)" }}>
        <div className="container">
          <AnimatedSection style={{ textAlign: "center", marginBottom: "4rem" }}>
            <span style={{
              display: "inline-block", padding: "4px 14px", borderRadius: "100px",
              background: "var(--primary-glow)", color: "var(--primary)",
              fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em",
              textTransform: "uppercase", marginBottom: "1rem",
            }}>
              Processus
            </span>
            <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1rem" }}>
              Prêt en 3 étapes simples
            </h2>
            <p style={{ fontSize: "1.05rem", color: "var(--text-secondary)", maxWidth: "500px", margin: "0 auto" }}>
              Pas de complication. Pas de paperasse. Juste votre numéro de téléphone.
            </p>
          </AnimatedSection>

          <StaggerContainer
            style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "2rem" }}
            staggerDelay={0.15}
          >
            {steps.map((s, i) => (
              <StaggerItem key={s.step}>
                <div style={{ position: "relative" }}>
                  {/* Connector line */}
                  {i < steps.length - 1 && (
                    <div style={{
                      position: "absolute",
                      top: "28px",
                      right: "-1rem",
                      width: "2rem",
                      height: "1px",
                      background: "linear-gradient(90deg, var(--primary), var(--border))",
                      display: "none",
                    }} className="step-connector" />
                  )}
                  <motion.div
                    whileHover={{ y: -4 }}
                    style={{
                      background: "var(--surface)",
                      border: "1px solid var(--border)",
                      borderRadius: "24px",
                      padding: "2.5rem 2rem",
                      textAlign: "center",
                      boxShadow: "var(--shadow-sm)",
                      height: "100%",
                    }}
                  >
                    <div style={{
                      width: "56px",
                      height: "56px",
                      borderRadius: "16px",
                      background: "linear-gradient(135deg, var(--primary), var(--primary-dark))",
                      color: "white",
                      fontSize: "1.1rem",
                      fontWeight: 900,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto 1.5rem",
                      boxShadow: "0 8px 20px var(--primary-glow)",
                      letterSpacing: "-0.04em",
                    }}>
                      {s.step}
                    </div>
                    <h3 style={{ fontWeight: 700, fontSize: "1.15rem", color: "var(--text)", marginBottom: "0.75rem", letterSpacing: "-0.02em" }}>
                      {s.title}
                    </h3>
                    <p style={{ color: "var(--text-secondary)", lineHeight: 1.7, fontSize: "0.9rem", marginBottom: "1rem" }}>
                      {s.desc}
                    </p>
                    <span style={{
                      display: "inline-block",
                      padding: "4px 12px",
                      borderRadius: "100px",
                      background: "var(--primary-glow)",
                      color: "var(--primary)",
                      fontSize: "0.75rem",
                      fontWeight: 600,
                    }}>
                      {s.detail}
                    </span>
                  </motion.div>
                </div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ====== TESTIMONIALS ====== */}
      <section style={{ padding: "7rem 0", background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
        <div className="container">
          <AnimatedSection style={{ textAlign: "center", marginBottom: "4rem" }}>
            <span style={{
              display: "inline-block", padding: "4px 14px", borderRadius: "100px",
              background: "var(--primary-glow)", color: "var(--primary)",
              fontSize: "0.75rem", fontWeight: 700, letterSpacing: "0.08em",
              textTransform: "uppercase", marginBottom: "1rem",
            }}>
              Témoignages
            </span>
            <h2 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "1rem" }}>
              Ce que disent nos agriculteurs
            </h2>
            <p style={{ fontSize: "1.05rem", color: "var(--text-secondary)", maxWidth: "480px", margin: "0 auto" }}>
              Des résultats concrets sur le terrain, mesurés par ceux qui l'utilisent.
            </p>
          </AnimatedSection>

          <StaggerContainer
            style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem" }}
            staggerDelay={0.1}
          >
            {testimonials.map((t) => (
              <StaggerItem key={t.name}>
                <motion.div
                  whileHover={{ y: -4, boxShadow: "var(--shadow-xl)" }}
                  style={{
                    background: "var(--bg)",
                    border: "1px solid var(--border)",
                    borderRadius: "20px",
                    padding: "2rem",
                    boxShadow: "var(--shadow-sm)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "1.25rem",
                  }}
                >
                  {/* Stars */}
                  <div style={{ display: "flex", gap: "3px" }}>
                    {[1,2,3,4,5].map((s) => (
                      <svg key={s} width="16" height="16" viewBox="0 0 24 24" fill={t.color} stroke="none">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                      </svg>
                    ))}
                  </div>

                  {/* Quote */}
                  <p style={{ color: "var(--text)", fontSize: "0.925rem", lineHeight: 1.75, fontStyle: "italic", margin: 0 }}>
                    "{t.quote}"
                  </p>

                  {/* Author */}
                  <div style={{ display: "flex", alignItems: "center", gap: "12px", borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
                    <img
                      src={t.photo}
                      alt={t.name}
                      style={{
                        width: "44px",
                        height: "44px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        flexShrink: 0,
                        border: `2px solid ${t.color}40`,
                      }}
                    />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "var(--text)" }}>{t.name}</div>
                      <div style={{ fontSize: "0.775rem", color: "var(--text-muted)" }}>{t.role} · {t.region}</div>
                    </div>
                  </div>
                </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* ====== CTA FINAL ====== */}
      <section style={{ padding: "7rem 0", background: "var(--bg)" }}>
        <div className="container">
          <AnimatedSection>
            <div style={{
              background: "linear-gradient(135deg, #052e16 0%, #14532d 50%, #15803d 100%)",
              borderRadius: "32px",
              padding: "clamp(3rem, 6vw, 5rem) clamp(2rem, 5vw, 4rem)",
              textAlign: "center",
              position: "relative",
              overflow: "hidden",
            }}>
              {/* Background grid */}
              <div style={{
                position: "absolute",
                inset: 0,
                backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
                backgroundSize: "40px 40px",
                borderRadius: "32px",
              }} />
              {/* Glow */}
              <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: "600px", height: "400px", background: "radial-gradient(ellipse, rgba(34,197,94,0.12) 0%, transparent 70%)", pointerEvents: "none" }} />

              <div style={{ position: "relative", zIndex: 1 }}>
                <h2 style={{ fontSize: "clamp(2rem, 4vw, 3rem)", fontWeight: 900, color: "white", letterSpacing: "-0.04em", marginBottom: "1.25rem", lineHeight: 1.1 }}>
                  Prêt à moderniser<br />votre agriculture ?
                </h2>
                <p style={{ fontSize: "1.1rem", color: "rgba(255,255,255,0.7)", marginBottom: "2.5rem", maxWidth: "480px", margin: "0 auto 2.5rem", lineHeight: 1.7 }}>
                  Rejoignez les agriculteurs togolais qui font confiance à Haroo pour développer leur activité.
                </p>
                <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
                  <motion.button
                    whileHover={{ scale: 1.03, boxShadow: "0 20px 40px rgba(34,197,94,0.4)" }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => navigate("/register")}
                    style={{
                      background: "linear-gradient(135deg, #22c55e, #16a34a)",
                      color: "white",
                      border: "none",
                      padding: "16px 36px",
                      borderRadius: "14px",
                      fontSize: "1.05rem",
                      fontWeight: 700,
                      cursor: "pointer",
                      boxShadow: "0 8px 24px rgba(22,163,74,0.4)",
                    }}
                  >
                    Commencer gratuitement →
                  </motion.button>
                  <motion.button
                    whileHover={{ background: "rgba(255,255,255,0.15)" }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => navigate("/documents")}
                    style={{
                      background: "rgba(255,255,255,0.08)",
                      color: "white",
                      border: "1px solid rgba(255,255,255,0.2)",
                      padding: "16px 32px",
                      borderRadius: "14px",
                      fontSize: "1.05rem",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Voir le catalogue
                  </motion.button>
                </div>

                <div style={{ marginTop: "2rem", color: "rgba(255,255,255,0.4)", fontSize: "0.8rem" }}>
                  Aucune carte bancaire requise · Paiement Mobile Money uniquement
                </div>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* ====== FOOTER ====== */}
      <footer style={{ background: "var(--surface)", borderTop: "1px solid var(--border)", padding: "3rem 0 2rem" }}>
        <div className="container">
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "3rem", marginBottom: "3rem" }}>
            {/* Brand */}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "1rem" }}>
                <div style={{ width: "32px", height: "32px", borderRadius: "8px", background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
                    <path d="M16 4C10 4 7 8.5 7 13c0 3.5 2.5 6.5 5.5 8.5L16 28l3.5-6.5C22.5 19.5 25 16.5 25 13c0-4.5-3-9-9-9z" fill="white" opacity="0.9"/>
                    <circle cx="16" cy="12" r="3.5" fill="white"/>
                  </svg>
                </div>
                <span style={{ fontWeight: 800, fontSize: "1.1rem", color: "var(--text)", letterSpacing: "-0.03em" }}>Haroo</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", lineHeight: 1.7, maxWidth: "280px" }}>
                La plateforme agricole intelligente du Togo. Documents, agronomes, analyses — tout pour moderniser votre agriculture.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 style={{ fontWeight: 700, fontSize: "0.875rem", color: "var(--text)", marginBottom: "1rem", letterSpacing: "0.02em", textTransform: "uppercase" }}>Services</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {[["Documents", "/documents"], ["Agronomes", "/agronomists"], ["Connexion", "/login"], ["Inscription", "/register"]].map(([label, to]) => (
                  <Link key={to} to={to} style={{ color: "var(--text-secondary)", fontSize: "0.875rem", fontWeight: 500, transition: "color 0.15s" }}
                    onMouseEnter={(e) => (e.currentTarget as HTMLElement).style.color = "var(--primary)"}
                    onMouseLeave={(e) => (e.currentTarget as HTMLElement).style.color = "var(--text-secondary)"}
                  >
                    {label}
                  </Link>
                ))}
              </div>
            </div>

            {/* Contact */}
            <div>
              <h4 style={{ fontWeight: 700, fontSize: "0.875rem", color: "var(--text)", marginBottom: "1rem", letterSpacing: "0.02em", textTransform: "uppercase" }}>Couverture</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {["Région des Savanes", "Région de la Kara", "Région Centrale", "Région des Plateaux", "Région Maritime"].map((r) => (
                  <span key={r} style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>{r}</span>
                ))}
              </div>
            </div>
          </div>

          <div style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
            <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>
              © 2026 Haroo. Tous droits réservés.
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>
              Conçu pour les agriculteurs togolais
            </span>
          </div>
        </div>
      </footer>

      {/* Responsive footer grid */}
      <style>{`
        @media (max-width: 768px) {
          footer .container > div:first-child {
            grid-template-columns: 1fr !important;
            gap: 2rem !important;
          }
        }
      `}</style>
    </div>
  );
}
