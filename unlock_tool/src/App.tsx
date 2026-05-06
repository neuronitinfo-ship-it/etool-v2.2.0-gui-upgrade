import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import EdlLoader from "./pages/tools/EdlLoader";
import AdbEnabler from "./pages/tools/AdbEnabler";
import BootDownload from "./pages/tools/BootDownload";
import Keygen from "./pages/tools/Keygen";
import QcDiag from "./pages/tools/QcDiag";
import Settings from "./pages/Settings";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/tools/edl-loader" element={<EdlLoader />} />
          <Route path="/tools/adb-enabler" element={<AdbEnabler />} />
          <Route path="/tools/boot-download" element={<BootDownload />} />
          <Route path="/tools/keygen" element={<Keygen />} />
          <Route path="/tools/qc-diag" element={<QcDiag />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
