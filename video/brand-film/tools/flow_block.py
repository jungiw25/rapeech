# scenes.py 안으로 들어가는 AI 원테이크 장면 블록(이 파일은 scenes.py가 exec 한다)
# ================================================================ flow: AI 콜봇 원테이크 (35 s)
LY = 540
CUST = 240
ST = [960, 1860, 2760, 3660, 4560]
FLOW_DUR = 35
# 단계별 도착 시각(장면 기준 초). 띠링 효과음도 이 값을 쓴다
ARR = [9.7, 13.6, 17.2, 20.8, 24.4]
TRV = [None, 12.2, 15.8, 19.4, 23.0]
RET_ARR = 30.0

cards = [
    ("음성 인식", "“카드를 잃어버렸어요”", False),
    ("의도 파악", "카드 분실 신고", False),
    ("목소리 인증", "본인 확인 완료", True),
    ("업무 처리", "카드 사용 정지", True),
    ("음성 응답", "답변을 목소리로", False),
]
CHECK = '<svg class="f-ck" width="34" height="34" viewBox="0 0 34 34" style="margin-left:14px;vertical-align:-5px"><circle cx="17" cy="17" r="16" fill="url(#fck)"/><path d="M10 17.5 l5 5 l9 -11" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="fck" x1="0" y1="0" x2="34" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset="1" stop-color="#3c24f3"/></linearGradient></defs></svg>'
card_html = ""
for i, (lab, val, ok) in enumerate(cards):
    chars = "".join(f'<b class="f-c{i}" style="display:inline-block;font-weight:700">{"&nbsp;" if c == " " else c}</b>' for c in val)
    card_html += f'''
        <div class="f-wrap" style="left:{ST[i]}px;top:{LY + 80}px"><div class="f-card" id="f-card{i}">
          <div class="f-cl">{lab}</div>
          <div class="f-cv">{chars}{CHECK if ok else ""}</div>
        </div></div>'''

# 고객(사람 + 스마트폰)
PHX, PHY = CUST + 185, LY - 40   # 휴대폰 중심(말하는 사람 앞, 떨어뜨려 둠)
cust = f'''
  <g id="f-cust">
    <g id="f-av">
      <circle cx="{CUST - 6}" cy="{LY - 36}" r="150" fill="url(#f-avglow)"/>
      <image href="assets/emoji/speaking_head_lit.png" x="{CUST - 130}" y="{LY - 166}" width="260" height="260"/>
    </g>
    <g id="f-phone">
      <rect x="{PHX - 25}" y="{PHY - 46}" width="50" height="92" rx="11" fill="url(#flow-g)" filter="url(#flow-glows)"/>
      <rect x="{PHX - 19}" y="{PHY - 38}" width="38" height="70" rx="6" fill="#0c0916" opacity=".5"/>
      {"".join(f'<rect x="{PHX - 11 + j * 8}" y="{PHY - 8 - (6, 12, 8)[j]}" width="5" height="{2 * (6, 12, 8)[j]}" rx="2.5" fill="#fff"/>' for j in range(3))}
      <rect x="{PHX - 7}" y="{PHY + 36}" width="14" height="3" rx="1.5" fill="#fff" opacity=".7"/>
    </g>
    <g id="f-rings">{"".join(f'<path class="f-ring" d="M{PHX + 31} {PHY - 52 - (20 + j * 16)} A {20 + j * 16} {20 + j * 16} 0 0 1 {PHX + 31 + 20 + j * 16} {PHY - 52}" fill="none" stroke="#ff4fd8" stroke-width="4" stroke-linecap="round"/>' for j in range(3))}</g>
    <g id="f-hit"><circle id="f-hglow" cx="{CUST - 6}" cy="{LY - 36}" r="150" fill="url(#f-avglow)" opacity="0"/>
      <circle class="f-hr" cx="{CUST - 6}" cy="{LY - 36}" r="118" fill="none" stroke="url(#flow-g)" stroke-width="4" opacity="0"/>
      <circle class="f-hr" cx="{CUST - 6}" cy="{LY - 36}" r="118" fill="none" stroke="#fff" stroke-width="2" opacity="0"/></g>
  </g>'''

nodes = "".join(
    f'''<g class="f-node" id="f-n{i}">
      <circle class="f-npulse o" id="f-np{i}" cx="{x}" cy="{LY}" r="36" fill="none" stroke="#ff4fd8" stroke-width="3"/>
      <circle cx="{x}" cy="{LY}" r="30" fill="#1c1730" stroke="#4a4166" stroke-width="3"/>
      <circle class="f-nfill o" id="f-nf{i}" cx="{x}" cy="{LY}" r="30" fill="url(#flow-g)" filter="url(#flow-glow)"/>
      <circle class="f-ncore o" id="f-nc{i}" cx="{x}" cy="{LY}" r="11" fill="#fff"/>
    </g>''' for i, x in enumerate(ST[:4]))

# AI 콜봇(마지막 단계)
bx = ST[4]
bot = f'''<g id="f-bot">
    <circle class="f-npulse o" id="f-np4" cx="{bx}" cy="{LY}" r="74" fill="none" stroke="#ff4fd8" stroke-width="3"/>
    <circle cx="{bx}" cy="{LY}" r="66" fill="#1c1730" stroke="#4a4166" stroke-width="3"/>
    <circle class="o" id="f-nf4" cx="{bx}" cy="{LY}" r="66" fill="url(#flow-g)" filter="url(#flow-glow)"/>
    <path d="M{bx - 40} {LY + 4} a40 40 0 0 1 80 0" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
    <rect x="{bx - 50}" y="{LY - 6}" width="16" height="30" rx="7" fill="#fff"/><rect x="{bx + 34}" y="{LY - 6}" width="16" height="30" rx="7" fill="#fff"/>
    <path d="M{bx + 42} {LY + 24} q 0 22 -28 24" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
    <text x="{bx}" y="{LY + 22}" text-anchor="middle" font-family="Pretendard" font-weight="800" font-size="34" fill="#fff">AI</text>
    {"".join(f'<rect class="f-bw o" x="{bx + 96 + j * 16}" y="{LY - 40}" width="8" height="80" rx="4" fill="{G[min(11, 4 + j)]}"/>' for j in range(6))}
  </g>'''

# 상담사(복잡한 상담 연결)
ax, ay = ST[3], LY + 330
agent = f'''<g id="f-agent">
    <path id="f-branch" d="M{ax} {LY + 30} L{ax} {ay - 86}" stroke="#9d79ff" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round" fill="none"/>
    <circle cx="{ax}" cy="{ay}" r="120" fill="url(#f-avglow)"/>
    <image href="assets/emoji/agent_headset_lit.png" x="{ax - 90}" y="{ay - 80}" width="180" height="180"/>
    <text x="{ax + 110}" y="{ay + 22}" font-family="Pretendard" font-weight="700" font-size="40" fill="#fff">상담사</text>
  </g>'''

# 목소리 묶음(선을 타고 이동)
packet = f'''<g id="f-pk"><rect id="f-pkr" x="-56" y="-24" width="112" height="48" rx="24" fill="url(#flow-g)" filter="url(#flow-glow)"/>
    {"".join(f'<rect class="f-pb o" x="{-30 + j * 13}" y="-15" width="6" height="30" rx="3" fill="#fff"/>' for j in range(5))}</g>'''

ret = '<path id="f-ret" d="__RETD__" fill="none" stroke="url(#flow-g)" stroke-width="5" stroke-linecap="round" filter="url(#flow-glows)"/>'
retpk = '<g id="f-rpk"><circle r="16" fill="#fff" filter="url(#flow-glows)"/></g>'

world_svg = (f'<svg width="5200" height="1400" viewBox="0 0 5200 1400" style="position:absolute;left:0;top:0;overflow:visible">'
             f'<defs><linearGradient id="flow-g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'
             f'<linearGradient id="f-skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f1ff"/><stop offset="1" stop-color="#b3a2f0"/></linearGradient>'
             f'<radialGradient id="f-avglow"><stop offset="0" stop-color="#6a4dff" stop-opacity=".35"/><stop offset="1" stop-color="#6a4dff" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="flow-rail" x1="300" y1="0" x2="4600" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'
             f'<filter id="flow-glow" filterUnits="userSpaceOnUse" x="-500" y="-500" width="6400" height="2400"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
             f'<filter id="flow-glows" filterUnits="userSpaceOnUse" x="-500" y="-500" width="6400" height="2400"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
             f'<path id="f-railL" d="M{ST[0]} {LY} L{PHX + 40} {LY}" stroke="url(#flow-rail)" stroke-width="6" stroke-linecap="round" filter="url(#flow-glows)" fill="none"/>'
             f'<path id="f-railR" d="M{ST[0]} {LY} L{bx - 66} {LY}" stroke="url(#flow-rail)" stroke-width="6" stroke-linecap="round" filter="url(#flow-glows)" fill="none"/>'
             + agent + ret + nodes + bot + cust + packet + retpk + '</svg>')

# 마지막에 모이는 빛 막대(다음 장면 서버 랙 LED의 확대 모습과 같음)
BAR = (f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;overflow:visible">'
       f'<defs><linearGradient id="__ID__-bg" x1="{960 - 184 * C30:.0f}" y1="0" x2="{960 + 184 * C30:.0f}" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset=".5" stop-color="#a518a4"/><stop offset="1" stop-color="#3c24f3"/></linearGradient>'
       f'<filter id="__ID__-bgl" filterUnits="userSpaceOnUse" x="-200" y="-200" width="2320" height="1480"><feGaussianBlur stdDeviation="36" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
       f'<path id="__ID__" d="M{960 - 184 * C30:.1f} {540 - 184 * S30:.1f} L{960 + 184 * C30:.1f} {540 + 184 * S30:.1f}" stroke="url(#__ID__-bg)" stroke-width="63" stroke-linecap="round" filter="url(#__ID__-bgl)" fill="none"/></svg>')

caps = [
    ("cA", "모든 대화는, [목소리]에서 시작합니다"),
    ("cB", "고객이 [전화]를 걸면"),
    ("c1", "AI 콜봇이 목소리를 듣고 [글로 옮기고]"),
    ("c2", "무엇을 원하는지 [이해한 뒤]"),
    ("c3", "[목소리로] 본인을 확인하고"),
    ("c4", "필요한 업무를 [바로 처리합니다]"),
    ("c5", "그리고 다시, [목소리로 답합니다]"),
    ("cP", "단순한 문의는 [AI 콜봇]이, 깊은 상담은 [상담사]가"),
]
cap_html = "".join(say(t, 60, 0, 150, f"f{cid}", extra="width:1920px;text-align:center") for cid, t in caps)

flow_css = f"""
    #f-world {{ position: absolute; left: 0; top: 0; width: 5200px; height: 1400px; }}
    .f-wrap {{ position: absolute; width: 0; display: flex; justify-content: center; }}
    .f-card {{ position: relative; flex: none; text-align: center; padding: 26px 40px; border-radius: 22px; background: rgba(28,23,48,.92); border: 1.5px solid #3a3158; }}
    .f-cl {{ font-size: 28px; font-weight: 600; color: {SUB}; }}
    .f-cv {{ margin-top: 10px; font-size: 40px; font-weight: 700; color: #fff; letter-spacing: -0.02em; white-space: nowrap; }}
    .f-bub {{ position: relative; flex: none; height: 92px; padding: 0 40px; border-radius: 46px; display: flex; align-items: center; font-size: 38px; font-weight: 700; white-space: nowrap; }}
"""
flow_body = f"""
      <div id="f-dark" style="position:absolute;inset:0;background:{DARK}"></div>
      <div class="vig"></div>
      <div id="f-light" style="position:absolute;inset:0;background:{LIGHT}"></div>
      <div id="f-iris" style="position:absolute;inset:0;background:{DARK}"></div>
      <div id="f-world">
        {world_svg}
        {card_html}
        <div class="f-wrap" style="left:{CUST}px;top:{LY - 320}px"><div class="f-bub" id="f-cbub" style="background:#fff;color:{INK}">카드를 잃어버렸어요</div></div>
        <div class="f-wrap" style="left:{bx}px;top:{LY - 250}px"><div class="f-bub" id="f-bbub" style="background:linear-gradient(100deg,#ff03c8,#a518a4 50%,#3c24f3);color:#fff">본인 확인이 끝나 카드 사용을 정지했어요</div></div>
      </div>
      <img id="f-sym" src="assets/brand/symbol_purple.svg" style="position:absolute;left:{SYM_X:.1f}px;top:{SYM_Y:.1f}px;width:{84 * SYM_S:.1f}px;height:{90 * SYM_S:.1f}px" />
      <img id="f-last" src="assets/intro_last.png" style="position:absolute;left:0;top:0;width:1920px;height:1080px" />
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;overflow:visible"><circle id="f-dot" class="o" cx="960" cy="540" r="16" fill="url(#fdg)"/><defs><linearGradient id="fdg" x1="944" y1="0" x2="976" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff03c8"/><stop offset="1" stop-color="#3c24f3"/></linearGradient></defs></svg>
      <div id="f-barwrap" style="position:absolute;inset:0">{BAR.replace("__ID__", "f-bar")}</div>
      {cap_html}
"""
SYM_CX, SYM_CY = SYM_X + 42 * SYM_S, SYM_Y + 47 * SYM_S
flow_js = """
      const ST = __ST__, ARR = __ARR__, TRV = __TRV__, LY = __LY__;
      const CAP = (id, tin, tout) => { IN("." + id + "-w", tin, { y: 0, b: 14, d: 1.0, s: 0.07 }); if (tout) OUT("." + id + "-w", tout, { y: 0, d: 0.6, s: 0.025 }); };
      gsap.set(["#f-nf0", "#f-nf1", "#f-nf2", "#f-nf3", "#f-nf4", "#f-nc0", "#f-nc1", "#f-nc2", "#f-nc3", ".f-npulse", ".f-hr"], { opacity: 0 });
      gsap.set("#f-pk", { x: 300, y: LY, opacity: 0 });
      gsap.set("#f-rpk", { opacity: 0 });
      gsap.set(".f-card", { opacity: 0 });
      gsap.set(".f-ck", { opacity: 0 });
      gsap.set(["#f-cbub", "#f-bbub", "#f-bar"], { opacity: 0 });
      gsap.set(["#f-agent"], { opacity: 0 });
      gsap.set("#f-world", { transformOrigin: "0px 0px" });

      // ── A. 로고가 그대로 있다가 → 워드마크가 사라지고 → 심볼이 작은 점으로 → 점에서 선이 뻗어 나감
      tl.to("#f-last", { opacity: 0, duration: 0.9, ease: "sine.inOut" }, 0.4);
      tl.to("#f-sym", { x: __DX__, y: __DY__, scale: 0.07, duration: 1.3, ease: "power3.inOut" }, 1.15);
      tl.to("#f-sym", { opacity: 0, duration: 0.35, ease: "sine.in" }, 2.1);
      tl.fromTo("#f-dot", { scale: 0.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.6, ease: "power2.out" }, 2.0);
      // 점을 중심으로 어둠이 원형으로 퍼짐(회색으로 탁해지지 않게)
      tl.fromTo("#f-iris", { clipPath: "circle(0% at 50% 50%)" }, { clipPath: "circle(75% at 50% 50%)", duration: 1.5, ease: "power2.inOut" }, 2.25);
      DRAW("#f-railR", 2.95, 2.4, "power2.inOut");
      DRAW("#f-railL", 3.05, 1.2, "power2.inOut");
      tl.to("#f-dot", { opacity: 0, duration: 0.5, ease: "sine.inOut" }, 3.5);
      tl.fromTo("#f-n0", { scale: 0.4, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.9, ease: "back.out(1.4)" }, 3.45);
      tl.fromTo(["#f-n1", "#f-n2", "#f-n3", "#f-bot"], { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "sine.inOut" }, 3.4);
      CAP("fcA", 3.3, 5.9);
      // 고객 등장(선의 시작점)
      tl.fromTo("#f-av", { opacity: 0, scale: 0.85, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 1.1, ease: "power3.out" }, 3.7);
      tl.fromTo("#f-phone", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 1.0, ease: "power3.out" }, 4.2);

      // ── B. 고객이 전화를 걺: 휴대폰 진동 + 울림
      CAP("fcB", 6.3, 9.5);
      for (let k = 0; k < 8; k++) tl.to("#f-phone", { rotation: k % 2 ? 7 : -7, svgOrigin: "__PX__ __PY__", duration: 0.09, ease: "sine.inOut" }, 6.0 + k * 0.09);
      tl.to("#f-phone", { rotation: 0, svgOrigin: "__PX__ __PY__", duration: 0.2, ease: "sine.out" }, 6.72);
      for (let k = 0; k < 8; k++) tl.to("#f-phone", { rotation: k % 2 ? 7 : -7, svgOrigin: "__PX__ __PY__", duration: 0.09, ease: "sine.inOut" }, 7.05 + k * 0.09);
      tl.to("#f-phone", { rotation: 0, svgOrigin: "__PX__ __PY__", duration: 0.2, ease: "sine.out" }, 7.77);
      tl.fromTo(".f-ring", { opacity: 0, x: -6, y: 6 }, { opacity: 1, x: 4, y: -4, duration: 0.5, ease: "sine.out", stagger: 0.1 }, 6.0);
      tl.to(".f-ring", { opacity: 0, x: 11, y: -11, duration: 0.5, ease: "sine.in", stagger: 0.1 }, 6.6);
      tl.fromTo(".f-ring", { opacity: 0, x: -6, y: 6 }, { opacity: 1, x: 4, y: -4, duration: 0.5, ease: "sine.out", stagger: 0.1, immediateRender: false }, 7.12);
      tl.to(".f-ring", { opacity: 0, x: 11, y: -11, duration: 0.5, ease: "sine.in", stagger: 0.1 }, 7.65);
      // 고객의 말
      tl.fromTo("#f-cbub", { opacity: 0, y: 20, scale: 0.9, filter: "blur(10px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }, 7.8);
      tl.to("#f-cbub", { opacity: 0.35, duration: 0.8, ease: "sine.inOut" }, 11.0);

      // 목소리 묶음: 휴대폰에서 나와 선을 타고 단계마다 이동
      const wig = (t0, t1) => { gsap.utils.toArray(".f-pb").forEach((el, j) => { let t = t0, s = j * 977 + 7; while (t < t1) { s = (s * 1664525 + 1013904223) % 4294967296; tl.to(el, { scaleY: 0.35 + 0.65 * s / 4294967296, duration: 0.16, ease: "sine.inOut" }, t); t += 0.16; } }); };
      const CAPS = { x: -56, y: -24, width: 112, height: 48, rx: 24 };
      const CIRC = (R) => ({ x: -R, y: -R, width: 2 * R, height: 2 * R, rx: R });
      tl.fromTo("#f-pk", { x: __PX__, y: __PY__, scale: 0.3, opacity: 0 }, { x: __PX__ + 70, y: LY, scale: 1, opacity: 1, duration: 0.7, ease: "power3.inOut" }, 8.3);
      tl.to("#f-pk", { x: ST[0], duration: 0.75, ease: "power2.inOut" }, 9.0 - 0.05);
      wig(8.4, ARR[0] - 0.85);
      // 도착: 캡슐이 노드 크기의 원으로 줄어들며 겹치고, 노드가 그 빛을 이어받아 켜짐(띠링)
      const arrive = (i, t) => {
        const R = i < 4 ? 30 : 66;
        tl.to("#f-pkr", { attr: CIRC(R), duration: 0.55, ease: "power2.inOut" }, t - 0.8);
        tl.to(".f-pb", { opacity: 0, duration: 0.25, ease: "sine.in" }, t - 0.8);
        tl.fromTo("#f-nf" + i, { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "sine.out" }, t);
        tl.to("#f-pk", { opacity: 0, duration: 0.18, ease: "sine.inOut" }, t + 0.04);
        tl.fromTo("#f-nf" + i, { scale: 1 }, { scale: 1.14, duration: 0.22, ease: "power2.out", yoyo: true, repeat: 1 }, t + 0.02);
        if (i < 4) tl.fromTo("#f-nc" + i, { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.8)" }, t + 0.12);
        tl.fromTo("#f-np" + i, { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 2.4, duration: 1.1, ease: "power2.out" }, t);
        tl.fromTo("#f-card" + i, { opacity: 0, y: 26, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }, t + 0.15);
        tl.fromTo(".f-c" + i, { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "power2.out", stagger: 0.045 }, t + 0.45);
        // 체크 표시는 글자가 다 나타난 다음 순서로
        const ck = document.querySelector("#f-card" + i + " .f-ck");
        if (ck) tl.fromTo(ck, { opacity: 0, scale: 0.3, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)", immediateRender: false }, t + 0.45 + gsap.utils.toArray(".f-c" + i).length * 0.045 + 0.35);
      };
      // 출발: 노드에서 같은 원으로 다시 나와 캡슐로 늘어나며 이동
      const depart = (i, t) => {
        tl.set("#f-pk", { x: ST[i - 1], opacity: 1 }, t);
        tl.set("#f-pkr", { attr: CIRC(30) }, t);
        tl.to("#f-pkr", { attr: CAPS, duration: 0.5, ease: "power2.out" }, t + 0.05);
        tl.to(".f-pb", { opacity: 1, duration: 0.3, ease: "sine.out" }, t + 0.3);
      };
      arrive(0, ARR[0]);
      CAP("fc1", 10.1, 12.0);
      // 다음 단계들: 카메라가 목소리를 따라 이동(원테이크)
      const caps = [null, ["fc2", 15.6], ["fc3", 19.2], ["fc4", 22.8], ["fc5", 26.8]];
      for (let i = 1; i < 5; i++) {
        const t = TRV[i];
        tl.to("#f-card" + (i - 1), { opacity: 0.45, duration: 0.8, ease: "sine.inOut" }, t);
        depart(i, t);
        tl.to("#f-pk", { x: ST[i], duration: 1.4, ease: "power2.inOut" }, t);
        tl.to("#f-world", { x: -(ST[i] - 960), duration: 1.55, ease: "power2.inOut" }, t - 0.05);
        wig(t + 0.3, ARR[i] - 0.85);
        arrive(i, ARR[i]);
        CAP("fc" + (i + 1), t + 0.95, caps[i][1]);
      }
      // AI 콜봇이 목소리로 답함
      tl.fromTo("#f-bbub", { opacity: 0, y: 20, scale: 0.9, filter: "blur(10px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.9, ease: "power3.out" }, 24.8);
      gsap.utils.toArray(".f-bw").forEach((el, j) => { tl.fromTo(el, { scaleY: 0.1, opacity: 0 }, { scaleY: 0.5, opacity: 1, duration: 0.4, ease: "power2.out" }, 24.8 + j * 0.04); let t = 25.2, s = j * 311 + 5; while (t < 26.8) { s = (s * 1664525 + 1013904223) % 4294967296; tl.to(el, { scaleY: 0.2 + 0.8 * s / 4294967296, duration: 0.18, ease: "sine.inOut" }, t); t += 0.18; } tl.to(el, { scaleY: 0.1, opacity: 0, duration: 0.4, ease: "power2.in" }, 26.8); });

      // ── C. 카메라가 뒤로 빠지며 전체 과정이 한눈에 / 답이 고객에게 돌아감 / 상담사 연결
      tl.to(".f-card", { opacity: 1, duration: 0.8, ease: "sine.inOut" }, 26.9);
      tl.to("#f-cbub", { opacity: 1, duration: 0.8, ease: "sine.inOut" }, 26.9);
      tl.to("#f-world", { x: __PBX__, y: __PBY__, scale: __PBS__, transformOrigin: "0px 0px", duration: 2.4, ease: "power3.inOut" }, 27.0);
      CAP("fcP", 28.6, 32.4);
      tl.fromTo("#f-rpk", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 28.3);
      tl.to("#f-rpk", { motionPath: null, duration: 0 }, 28.3);
      const RP = __RETPTS__;
      gsap.set("#f-rpk", { x: RP[0][0], y: RP[0][1] });
      // 선은 점이 지나간 자리까지만 정확히 그려짐(점과 선 사이 틈 없음, 선이 앞서지 않음)
      const RL = [0]; for (let k = 1; k < RP.length; k++) RL.push(RL[k - 1] + Math.hypot(RP[k][0] - RP[k - 1][0], RP[k][1] - RP[k - 1][1]));
      const RT = RL[RL.length - 1], ret = document.querySelector("#f-ret");
      ret.setAttribute("stroke-dasharray", `${RT + 10} ${RT + 10}`);
      // 시작 전에는 선 끝(둥근 꼭지)도 보이지 않게: 오프셋을 한 칸 더 밀고, 움직이기 전까지 숨김
      gsap.set(ret, { attr: { "stroke-dashoffset": RT + 10 }, opacity: 0 });
      tl.set(ret, { opacity: 1 }, 28.3);
      for (let k = 1; k < RP.length; k++) {
        const d = 1.7 / (RP.length - 1), t = 28.3 + d * (k - 1);
        tl.to("#f-rpk", { x: RP[k][0], y: RP[k][1], duration: d, ease: "none" }, t);
        tl.to(ret, { attr: { "stroke-dashoffset": RT + 10 - RL[k] }, duration: d, ease: "none" }, t);
      }
      tl.to("#f-rpk", { opacity: 0, scale: 2, duration: 0.4, ease: "power2.out" }, __RETARR__);
      // 도착: 점이 사람에게 닿으면 사람을 감싼 둥근 물결 두 겹이 퍼지고 고객 뒤의 빛이 잠깐 밝아짐(띠링)
      gsap.utils.toArray(".f-hr").forEach((el, k) => tl.fromTo(el, { opacity: 0.95, scale: 1, svgOrigin: "__HX__ __HY__" }, { opacity: 0, scale: 1.55, svgOrigin: "__HX__ __HY__", duration: 1.1, ease: "power2.out", immediateRender: false }, __RETARR__ + k * 0.14));
      tl.fromTo("#f-hglow", { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "sine.out", immediateRender: false }, __RETARR__);
      tl.to("#f-hglow", { opacity: 0, duration: 1.0, ease: "sine.inOut" }, __RETARR__ + 0.3);
      DRAW("#f-branch", 29.5, 0.9, "power2.inOut");
      tl.fromTo("#f-agent", { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "sine.inOut" }, 29.4);

      // ── D. 모든 빛이 작은 막대 하나로 모임 → 다음 장면(서버 랙의 LED 한 칸)
      tl.to("#f-world", { scale: __PBS2__, x: __PBX2__, y: __PBY2__, opacity: 0, duration: 1.4, ease: "power3.in" }, 32.6);
      tl.fromTo("#f-bar", { opacity: 0, scale: 0.05, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 1.3, ease: "power3.out" }, 33.5);
"""
# 풀백 배율·위치(세계 좌표 120..4700, 220..940을 화면에 맞춤)
PBS = 0.38
PBX = 960 - 2410 * PBS
PBY = 560 - 600 * PBS
PBS2 = 0.08
PBX2 = 960 - 2410 * PBS2
PBY2 = 540 - 600 * PBS2
# 되돌아가는 답(베지어를 점으로 샘플링)
# 답 말풍선의 왼쪽 끝에서 출발해 고객(사람) 머리 오른쪽 위에 닿음. 고객 말풍선과 휴대폰은 비켜 지나감
p0, c1, c2, p3 = (bx - 380, LY - 204), (bx - 1100, LY - 680), (CUST + 430, LY - 420), (CUST + 95, LY - 125)
RET = []
N = 72
for k in range(N + 1):
    v = k / N
    u = 4 * v ** 3 if v < 0.5 else 1 - (-2 * v + 2) ** 3 / 2
    x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u ** 3 * p3[0]
    y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u ** 3 * p3[1]
    RET.append([round(x, 1), round(y, 1)])
flow_js = (flow_js.replace("__ST__", json.dumps(ST)).replace("__ARR__", json.dumps(ARR)).replace("__TRV__", json.dumps(TRV)).replace("__LY__", str(LY))
           .replace("__DX__", f"{960 - SYM_CX:.1f}").replace("__DY__", f"{540 - SYM_CY:.1f}")
           .replace("__PX__", str(PHX)).replace("__PY__", str(PHY))
           .replace("__PBX__", f"{PBX:.1f}").replace("__PBY__", f"{PBY:.1f}").replace("__PBS__", str(PBS))
           .replace("__PBX2__", f"{PBX2:.1f}").replace("__PBY2__", f"{PBY2:.1f}").replace("__PBS2__", str(PBS2))
           .replace("__RETPTS__", json.dumps(RET)).replace("__HX__", str(CUST - 6)).replace("__HY__", str(LY - 36)).replace("__RETARR__", str(RET_ARR)))
flow_js = flow_js.replace('      tl.to("#f-rpk", { motionPath: null, duration: 0 }, 28.3);\n', "")
flow_body = flow_body.replace("__RETD__", "M" + " L".join(f"{x} {y}" for x, y in RET))
scene("flow", FLOW_DUR, flow_body, flow_js, css=flow_css)
FLOW_EVENTS = dict(arrive=ARR, travel=[t for t in TRV if t], ret=RET_ARR)
