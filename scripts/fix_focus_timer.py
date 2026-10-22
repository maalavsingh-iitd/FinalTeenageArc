from pathlib import Path

root = Path("final-teenage-arc-v2")
app_path = root / "src" / "App.jsx"
readme_path = root / "README.md"
source = app_path.read_text(encoding="utf-8")

if "function readFocusTimer()" not in source:
    def replace_once(old, new, label):
        global source
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"Expected exactly one match for {label}, found {count}; refusing to patch an unknown source version.")
        source = source.replace(old, new, 1)

    replace_once(
        'function IconButton({ children, onClick, title, className="" }) {',
        '''function readFocusTimer() {
  try {
    const saved = JSON.parse(localStorage.getItem("fta-focus-timer") || "null");
    return saved && typeof saved === "object" ? saved : {};
  } catch { return {}; }
}
function IconButton({ children, onClick, title, className="" }) {''',
        "timer storage reader",
    )
    replace_once(
        '''  const [clockNow,setClockNow] = useState(Date.now());
  const [focusMinutes,setFocusMinutes] = useState(50);
  const [focusSecondsLeft,setFocusSecondsLeft] = useState(50*60);
  const [focusRunning,setFocusRunning] = useState(false);
  const [focusLabel,setFocusLabel] = useState("Deep work");''',
        '''  const [clockNow,setClockNow] = useState(Date.now());
  const [focusMinutes,setFocusMinutes] = useState(()=>{const saved=readFocusTimer();return [25,50,90].includes(saved.minutes)?saved.minutes:50;});
  const [focusEndAt,setFocusEndAt] = useState(()=>{const saved=readFocusTimer();return saved.running&&Number.isFinite(saved.endAt)&&saved.endAt>Date.now()?saved.endAt:null;});
  const [focusSecondsLeft,setFocusSecondsLeft] = useState(()=>{const saved=readFocusTimer();if(saved.running&&Number.isFinite(saved.endAt))return Math.max(0,Math.ceil((saved.endAt-Date.now())/1000));return Number.isFinite(saved.remainingSeconds)?Math.max(0,Math.floor(saved.remainingSeconds)):50*60;});
  const [focusRunning,setFocusRunning] = useState(()=>{const saved=readFocusTimer();return Boolean(saved.running&&Number.isFinite(saved.endAt)&&saved.endAt>Date.now());});
  const [focusLabel,setFocusLabel] = useState(()=>{const saved=readFocusTimer();return typeof saved.label==="string"&&saved.label.trim()?saved.label:"Deep work";});''',
        "persisted timer state",
    )
    replace_once(
        '''  useEffect(()=>{ const timer=setInterval(()=>setClockNow(Date.now()),1000); return ()=>clearInterval(timer); },[]);
  useEffect(()=>{ if(!focusRunning) return; const timer=setInterval(()=>setFocusSecondsLeft(v=>{ if(v<=1){setFocusRunning(false);setToast("Focus session complete. Log what you accomplished.");return 0;} return v-1;}),1000); return ()=>clearInterval(timer); },[focusRunning]);''',
        '''  useEffect(()=>{
    const syncClock=()=>setClockNow(Date.now());
    const syncWhenVisible=()=>{if(document.visibilityState==="visible")syncClock();};
    syncClock();
    const timer=setInterval(syncClock,1000);
    window.addEventListener("focus",syncClock);
    window.addEventListener("pageshow",syncClock);
    document.addEventListener("visibilitychange",syncWhenVisible);
    return ()=>{clearInterval(timer);window.removeEventListener("focus",syncClock);window.removeEventListener("pageshow",syncClock);document.removeEventListener("visibilitychange",syncWhenVisible);};
  },[]);
  useEffect(()=>{
    if(!focusRunning||!focusEndAt)return;
    const updateRemaining=()=>{
      const remaining=Math.max(0,Math.ceil((focusEndAt-Date.now())/1000));
      setFocusSecondsLeft(current=>current===remaining?current:remaining);
      if(remaining===0){setFocusRunning(false);setFocusEndAt(null);setToast("Focus session time is up. Review and log what you accomplished.");}
    };
    updateRemaining();
    const timer=setInterval(updateRemaining,1000);
    window.addEventListener("focus",updateRemaining);
    window.addEventListener("pageshow",updateRemaining);
    document.addEventListener("visibilitychange",updateRemaining);
    return ()=>{clearInterval(timer);window.removeEventListener("focus",updateRemaining);window.removeEventListener("pageshow",updateRemaining);document.removeEventListener("visibilitychange",updateRemaining);};
  },[focusRunning,focusEndAt]);
  useEffect(()=>{
    try{
      const remaining=focusRunning&&focusEndAt?Math.max(0,Math.ceil((focusEndAt-Date.now())/1000)):focusSecondsLeft;
      localStorage.setItem("fta-focus-timer",JSON.stringify({minutes:focusMinutes,label:focusLabel,running:Boolean(focusRunning&&focusEndAt),endAt:focusRunning?focusEndAt:null,remainingSeconds:remaining}));
    }catch{}
  },[focusMinutes,focusLabel,focusSecondsLeft,focusRunning,focusEndAt]);''',
        "clock synchronization and persistence effects",
    )
    replace_once(
        '''  const finishFocusSession = () => {
    const spent=Math.max(0,Math.round((focusMinutes*60-focusSecondsLeft)/60));
    if(spent<1){setToast("Complete at least one minute before logging a session");return;}
    setFocusSessions(s=>[{id:Date.now(),label:focusLabel.trim()||"Focus session",minutes:spent,date:today},...s]);
    setFocusRunning(false);setFocusSecondsLeft(focusMinutes*60);setToast(`${spent} focused minutes logged`);
  };''',
        '''  const toggleFocusTimer = () => {
    if(focusRunning){
      const remaining=focusEndAt?Math.max(0,Math.ceil((focusEndAt-Date.now())/1000)):focusSecondsLeft;
      setFocusSecondsLeft(remaining);setFocusRunning(false);setFocusEndAt(null);return;
    }
    const remaining=focusSecondsLeft>0?focusSecondsLeft:focusMinutes*60;
    setFocusSecondsLeft(remaining);setFocusEndAt(Date.now()+remaining*1000);setFocusRunning(true);
  };
  const resetFocusTimer = () => {setFocusRunning(false);setFocusEndAt(null);setFocusSecondsLeft(focusMinutes*60);};
  const finishFocusSession = () => {
    const remaining=focusRunning&&focusEndAt?Math.max(0,Math.ceil((focusEndAt-Date.now())/1000)):focusSecondsLeft;
    const spent=Math.max(0,Math.round((focusMinutes*60-remaining)/60));
    if(spent<1){setToast("Complete at least one minute before logging a session");return;}
    setFocusSessions(s=>[{id:Date.now(),label:focusLabel.trim()||"Focus session",minutes:spent,date:today},...s]);
    setFocusRunning(false);setFocusEndAt(null);setFocusSecondsLeft(focusMinutes*60);setToast(`${spent} focused minutes logged`);
  };''',
        "focus controls and finish logging",
    )
    replace_once('onClick={()=>{setFocusMinutes(n);setFocusSecondsLeft(n*60)}}',
                 'onClick={()=>{setFocusMinutes(n);setFocusEndAt(null);setFocusSecondsLeft(n*60)}}',
                 "preset state")
    replace_once('onClick={()=>{if(focusSecondsLeft===0)setFocusSecondsLeft(focusMinutes*60);setFocusRunning(!focusRunning)}}',
                 'onClick={toggleFocusTimer}', "start/pause button")
    replace_once('onClick={()=>{setFocusRunning(false);setFocusSecondsLeft(focusMinutes*60)}}',
                 'onClick={resetFocusTimer}', "reset button")
    replace_once(
        "Timer runs while this page is open. If you leave the page, the session pauses only if you pause it manually; keep the tab open for the most reliable timing.",
        "The timer uses an absolute end time and catches up when you return, even after closing the browser. Your device cannot guarantee a sound or notification while the site is fully closed.",
        "timer help text")
    replace_once("This session history is kept in the current app session.",
                 "Your focus history is saved in this browser.", "history help text")
    app_path.write_text(source, encoding="utf-8")
    print("Applied absolute-timestamp focus timer patch.")
else:
    print("Focus timer fix already applied.")

readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    "- **Focus Mode:** 25-, 50-, and 90-minute sessions, pause/resume/reset, and a persisted session log.",
    "- **Focus Mode:** 25-, 50-, and 90-minute sessions. It uses an absolute end timestamp and persists running/paused state, so it catches up after a hidden tab or browser restart. Completed sessions are logged separately.")
readme = readme.replace(
    "- Focus timer is designed for a foreground browser tab; browser throttling or closing the tab can affect timer behavior.",
    "- While the site is closed, browser JavaScript is not running and notifications are not guaranteed. The focus timer recalculates from its saved end timestamp on return, but cannot guarantee an audible alert while fully closed.")
readme_path.write_text(readme, encoding="utf-8")
print("Updated focus timer documentation.")
