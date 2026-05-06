import { AppShell } from "@/components/layout/AppShell";
import { GlassCard } from "@/components/ui/glass-card";
import { Smartphone, Cpu, HardDrive, Wifi, Battery, CheckCircle2, XCircle, ArrowUpRight, Activity, Zap, Shield } from "lucide-react";
import { NavLink } from "react-router-dom";

const Index = () => {
  return (
    <AppShell title="Welcome Back">
      <div className="grid grid-cols-12 gap-5">
        {/* Device Panel - hero */}
        <div className="col-span-12 lg:col-span-8">
          <GlassCard className="p-6 relative overflow-hidden" hover={false}>
            <div className="absolute -right-10 -top-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl" />
            <div className="flex items-start justify-between mb-6 relative">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider">Connected Device</p>
                <h2 className="text-2xl font-semibold mt-1">Qualcomm SM8250 · EDL Mode</h2>
                <p className="text-sm text-muted-foreground mt-1">Sahara Protocol · Port COM7</p>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/15 text-success text-xs font-medium border border-success/20">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse-glow" />
                Online
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 relative">
              {[
                { icon: Cpu, label: "SoC", value: "SDM865" },
                { icon: HardDrive, label: "Storage", value: "256 GB" },
                { icon: Battery, label: "Battery", value: "82%" },
                { icon: Wifi, label: "Link", value: "USB 3.0" },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="glass rounded-2xl p-4">
                  <Icon className="w-4 h-4 text-primary mb-2" />
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className="text-sm font-semibold mt-0.5">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3 relative">
              <button className="bg-gradient-primary text-primary-foreground rounded-2xl py-3.5 font-medium glow-primary hover:scale-[1.02] transition">
                Read Info
              </button>
              <button className="glass-strong rounded-2xl py-3.5 font-medium hover:bg-white/5 transition">
                Reboot
              </button>
              <button className="col-span-2 rounded-2xl py-3.5 font-medium border border-destructive/30 bg-destructive/10 text-destructive hover:bg-destructive/15 transition">
                Disconnect
              </button>
            </div>
          </GlassCard>
        </div>

        {/* Side stats */}
        <div className="col-span-12 lg:col-span-4 space-y-5">
          <GlassCard title="Operations Today">
            <p className="text-3xl font-semibold">147</p>
            <p className="text-xs text-success mt-1 flex items-center gap-1">
              <ArrowUpRight className="w-3 h-3" /> 12% vs yesterday
            </p>
            <div className="mt-4 h-2 rounded-full bg-white/5 overflow-hidden">
              <div className="h-full bg-gradient-primary w-3/4 rounded-full" />
            </div>
          </GlassCard>

          <GlassCard title="System Status">
            <div className="space-y-3">
              {[
                { label: "USB Driver", ok: true },
                { label: "ADB Server", ok: true },
                { label: "Fastboot", ok: false },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{s.label}</span>
                  {s.ok ? <CheckCircle2 className="w-4 h-4 text-success" /> : <XCircle className="w-4 h-4 text-destructive" />}
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Quick tools */}
        <div className="col-span-12">
          <h3 className="text-sm font-semibold mb-3 px-1">Quick Tools</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              { to: "/tools/edl-loader", icon: HardDrive, title: "EDL Loader Parse", desc: "Extract firehose loaders" },
              { to: "/tools/adb-enabler", icon: Zap, title: "ADB Enabler", desc: "Unlock developer mode" },
              { to: "/tools/boot-download", icon: Smartphone, title: "Boot → Download", desc: "Force download mode" },
              { to: "/tools/keygen", icon: Shield, title: "Sierra Keygen", desc: "OEM unlock keys" },
              { to: "/tools/qc-diag", icon: Activity, title: "QC Diag", desc: "Qualcomm diagnostics" },
            ].map(({ to, icon: Icon, title, desc }) => (
              <NavLink key={to} to={to}>
                <GlassCard className="h-full">
                  <div className="w-10 h-10 rounded-xl bg-gradient-primary/20 border border-primary/30 flex items-center justify-center mb-3">
                    <Icon className="w-5 h-5 text-primary" />
                  </div>
                  <p className="font-medium text-sm">{title}</p>
                  <p className="text-xs text-muted-foreground mt-1">{desc}</p>
                </GlassCard>
              </NavLink>
            ))}
          </div>
        </div>

        {/* Recent activity */}
        <div className="col-span-12 lg:col-span-7">
          <GlassCard title="Recent Activity">
            <div className="space-y-3">
              {[
                { op: "Loader extracted", file: "msm8953_loader.elf", time: "2m ago", ok: true },
                { op: "ADB enabled", file: "Quectel EM7565", time: "18m ago", ok: true },
                { op: "Flash failed", file: "boot.img → /dev/sda", time: "1h ago", ok: false },
                { op: "Sierra keygen", file: "AT!OPENLOCK", time: "3h ago", ok: true },
              ].map((a, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.04] transition">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${a.ok ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive"}`}>
                      {a.ok ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{a.op}</p>
                      <p className="text-xs text-muted-foreground">{a.file}</p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">{a.time}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="col-span-12 lg:col-span-5">
          <GlassCard title="API Throughput">
            <p className="text-xs text-muted-foreground">Avg response · last 24h</p>
            <p className="text-3xl font-semibold mt-2">128<span className="text-base text-muted-foreground"> ms</span></p>
            <div className="mt-4 flex items-end gap-1.5 h-24">
              {[40, 65, 50, 80, 60, 90, 75, 55, 70, 85, 60, 95].map((h, i) => (
                <div key={i} className="flex-1 rounded-md bg-gradient-to-t from-primary/30 to-primary/80" style={{ height: `${h}%` }} />
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
};

export default Index;
