"""
简单的前端操作页（用于本地/测试对接）
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"], include_in_schema=False)


@router.get("/ui", response_class=HTMLResponse, include_in_schema=False)
async def ui_page():
    return HTMLResponse(
        content=_HTML,
        status_code=200,
        headers={"Cache-Control": "no-store"},
    )


_HTML = """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>VideoCreator UI</title>
    <style>
      :root {
        --bg: #0b1020;
        --panel: #111936;
        --muted: #93a4c7;
        --text: #eaf0ff;
        --border: rgba(255,255,255,.12);
        --accent: #6ea8fe;
        --danger: #ff6b6b;
        --ok: #51cf66;
        --warn: #ffd43b;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif;
        background: radial-gradient(1200px 500px at 30% -10%, rgba(110,168,254,.25), transparent 60%),
                    radial-gradient(900px 400px at 90% 10%, rgba(255,212,59,.15), transparent 55%),
                    var(--bg);
        color: var(--text);
      }
      header {
        padding: 20px 20px 10px;
        border-bottom: 1px solid var(--border);
        position: sticky;
        top: 0;
        backdrop-filter: blur(10px);
        background: rgba(11,16,32,.72);
        z-index: 10;
      }
      header h1 { margin: 0; font-size: 18px; letter-spacing: .2px; }
      header p { margin: 6px 0 0; color: var(--muted); font-size: 13px; }
      main { max-width: 1200px; margin: 0 auto; padding: 18px; }
      .grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 14px;
        align-items: start;
      }
      .card {
        grid-column: span 4;
        background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
      }
      .card h2 { margin: 0 0 10px; font-size: 15px; }
      .card small { color: var(--muted); }
      .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
      label { display: block; font-size: 12px; color: var(--muted); margin: 10px 0 6px; }
      label.fileBtn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px 16px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,.05);
        color: var(--text);
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
        margin: 0;
      }
      label.fileBtn:hover {
        background: rgba(255,255,255,.08);
        border-color: var(--accent);
      }
      label.fileBtn::before {
        content: "📁";
        font-size: 16px;
      }
      input, select, textarea, button {
        width: 100%;
        padding: 10px 10px;
        border-radius: 10px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,.03);
        color: var(--text);
        outline: none;
      }
      /* 隐藏原生文件选择按钮 */
      input[type="file"] {
        display: none;
      }
      textarea { min-height: 92px; resize: vertical; }
      input[type="checkbox"] { width: auto; transform: translateY(1px); }
      .checks { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; }
      .checks label { margin: 0; display: flex; gap: 8px; align-items: center; }
      button {
        cursor: pointer;
        background: linear-gradient(180deg, rgba(110,168,254,.25), rgba(110,168,254,.10));
        border: 1px solid rgba(110,168,254,.35);
        font-weight: 600;
      }
      button.secondary {
        background: rgba(255,255,255,.03);
        border: 1px solid var(--border);
        font-weight: 500;
      }
      button.danger {
        background: rgba(255,107,107,.12);
        border: 1px solid rgba(255,107,107,.35);
      }
      .card .actions { display: flex; gap: 10px; margin-top: 12px; }
      .card .actions button { width: auto; flex: 1; }
      .wide { grid-column: span 12; }
      .status {
        background: rgba(255,255,255,.03);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
        scroll-margin-top: 90px;
      }
      .statusTop { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
      .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        border: 1px solid var(--border);
        color: var(--muted);
      }
      .badge.ok { border-color: rgba(81,207,102,.45); color: rgba(187,247,208,.95); }
      .badge.warn { border-color: rgba(255,212,59,.45); color: rgba(255,244,193,.98); }
      .badge.bad { border-color: rgba(255,107,107,.45); color: rgba(255,199,199,.98); }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
      .muted { color: var(--muted); }
      .player {
        width: 100%;
        max-width: 920px;
        aspect-ratio: 16 / 9;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: rgba(0,0,0,.25);
        display: block;
        margin: 0 auto;
        scroll-margin-top: 90px;
      }
      .fileList { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
      .fileChip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,.03);
        max-width: 100%;
      }
      .fileName {
        font-size: 12px;
        max-width: 220px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .fileRemove {
        width: 24px;
        height: 24px;
        padding: 0;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,107,107,.12);
        border: 1px solid rgba(255,107,107,.35);
        font-weight: 700;
        line-height: 1;
      }
      .fileRemove:hover { filter: brightness(1.1); }
      .links a { color: var(--accent); text-decoration: none; word-break: break-all; }
      .links a:hover { text-decoration: underline; }
      pre {
        margin: 12px 0 0;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: rgba(0,0,0,.18);
        overflow: auto;
        max-height: 320px;
      }

      .tabs {
        margin-top: 14px;
        display: inline-flex;
        gap: 6px;
        padding: 6px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,.03);
      }
      .tab {
        width: auto;
        padding: 8px 12px;
        border-radius: 999px;
        border: 1px solid transparent;
        background: transparent;
        color: var(--muted);
        cursor: pointer;
        font-weight: 600;
        font-size: 13px;
      }
      .tab.active {
        color: var(--text);
        background: linear-gradient(180deg, rgba(110,168,254,.25), rgba(110,168,254,.10));
        border-color: rgba(110,168,254,.35);
      }
      .pages {
        display: flex;
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        border-radius: 14px;
      }
      .pages::-webkit-scrollbar { display: none; }
      .pages { scrollbar-width: none; }
      .page {
        flex: 0 0 100%;
        scroll-snap-align: start;
      }
      @media (max-width: 980px) { .card { grid-column: span 12; } }
    </style>
  </head>
  <body>
    <header>
      <h1>VideoCreator UI</h1>
      <div class="tabs" role="tablist" aria-label="模型选择">
        <button id="tab_wan" class="tab active" type="button">Wan2.6</button>
        <button id="tab_seedance" class="tab" type="button">Seedance1.5pro</button>
      </div>
    </header>

    <main>
      <div id="mode_pages" class="pages" aria-label="模型页面">
        <section id="page_wan" class="page" data-provider="wan">
          <div class="grid">
        <section class="card">
          <h2>T2V 文生视频</h2>
          <small>POST <span class="mono">/api/v1/video/t2v</span></small>
          <label>Prompt（必填）</label>
          <textarea id="t2v_prompt" placeholder="描述你想生成的视频..."></textarea>
          <div class="row">
            <div>
              <label>Size</label>
              <select id="t2v_size">
                <optgroup label="720P">
                  <option value="1280*720">1280*720（16:9）</option>
                  <option value="720*1280">720*1280（9:16）</option>
                  <option value="960*960">960*960（1:1）</option>
                  <option value="1088*832">1088*832（4:3）</option>
                  <option value="832*1088">832*1088（3:4）</option>
                </optgroup>
                <optgroup label="1080P">
                  <option value="1920*1080" selected>1920*1080（16:9）</option>
                  <option value="1080*1920">1080*1920（9:16）</option>
                  <option value="1440*1440">1440*1440（1:1）</option>
                  <option value="1632*1248">1632*1248（4:3）</option>
                  <option value="1248*1632">1248*1632（3:4）</option>
                </optgroup>
              </select>
            </div>
            <div>
              <label>Duration</label>
              <select id="t2v_duration">
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
              </select>
            </div>
          </div>
          <div class="row">
            <div>
              <label>Model</label>
              <input id="t2v_model" value="wan2.6-t2v" />
            </div>
            <div>
              <label>Shot Type</label>
              <select id="t2v_shot_type">
                <option value="single">single</option>
                <option value="multi">multi</option>
              </select>
            </div>
          </div>
          <label>Negative Prompt（可选）</label>
          <input id="t2v_negative_prompt" value="低质量，模糊，失焦，低分辨率，噪点，压缩伪影，闪烁，抖动，画面不稳定，运动模糊，畸形，错误结构，面部变形，多余或缺失肢体，手部错误，动作不自然，僵硬动画，过曝，欠曝，光照不一致，透视错误，物体扭曲，字幕" placeholder="不希望出现的内容..." />
          <label>Audio（可选，wav/mp3）</label>
          <input id="t2v_audio" type="file" accept="audio/*" />
          <label for="t2v_audio" class="fileBtn">选择音频文件</label>
          <div id="t2v_audio_list" class="fileList"></div>
          <div class="checks">
            <label><input id="t2v_prompt_extend" type="checkbox" checked /> prompt_extend</label>
            <label><input id="t2v_audio_enable" type="checkbox" checked /> audio_enable</label>
            <label><input id="t2v_watermark" type="checkbox" /> watermark</label>
          </div>
          <label>Seed（可选）</label>
          <input id="t2v_seed" type="number" min="0" max="2147483647" placeholder="留空使用随机" />
          <div class="actions">
            <button id="t2v_submit">创建任务</button>
          </div>
        </section>

        <section class="card">
          <h2>I2V 图生视频</h2>
          <small>POST <span class="mono">/api/v1/video/i2v</span></small>
          <label>Image（必填）</label>
          <input id="i2v_image" type="file" accept="image/*" />
          <label for="i2v_image" class="fileBtn">选择图片文件</label>
          <div id="i2v_image_list" class="fileList"></div>
          <label>Prompt（可选）</label>
          <textarea id="i2v_prompt" placeholder="如：保持主体一致，生成自然动作..."></textarea>
          <div class="row">
            <div>
              <label>Resolution</label>
              <select id="i2v_resolution">
                <option value="1080P">1080P</option>
                <option value="720P">720P</option>
              </select>
            </div>
            <div>
              <label>Duration</label>
              <select id="i2v_duration">
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
              </select>
            </div>
          </div>
          <div class="row">
            <div>
              <label>Model</label>
              <input id="i2v_model" value="wan2.6-i2v" />
            </div>
            <div>
              <label>Shot Type</label>
              <select id="i2v_shot_type">
                <option value="single">single</option>
                <option value="multi">multi</option>
              </select>
            </div>
          </div>
          <label>Negative Prompt（可选）</label>
          <input id="i2v_negative_prompt" value="低质量，模糊，失焦，低分辨率，噪点，压缩伪影，闪烁，抖动，画面不稳定，运动模糊，畸形，错误结构，面部变形，多余或缺失肢体，手部错误，动作不自然，僵硬动画，过曝，欠曝，光照不一致，透视错误，物体扭曲，字幕" placeholder="不希望出现的内容..." />
          <label>Audio（可选，wav/mp3）</label>
          <input id="i2v_audio" type="file" accept="audio/*" />
          <label for="i2v_audio" class="fileBtn">选择音频文件</label>
          <div id="i2v_audio_list" class="fileList"></div>
          <div class="checks">
            <label><input id="i2v_prompt_extend" type="checkbox" checked /> prompt_extend</label>
            <label><input id="i2v_audio_enable" type="checkbox" checked /> audio_enable</label>
            <label><input id="i2v_watermark" type="checkbox" /> watermark</label>
          </div>
          <label>Seed（可选）</label>
          <input id="i2v_seed" type="number" min="0" max="2147483647" placeholder="留空使用随机" />
          <div class="actions">
            <button id="i2v_submit">创建任务</button>
          </div>
        </section>

        <section class="card">
          <h2>R2V 参考生视频</h2>
          <small>POST <span class="mono">/api/v1/video/r2v</span></small>
          <label>Reference Videos（必填，最多3个）</label>
          <input id="r2v_videos" type="file" accept="video/*" multiple />
          <label for="r2v_videos" class="fileBtn">选择参考视频（最多3个）</label>
          <div id="r2v_video_list" class="fileList"></div>
          <label>Prompt（必填）</label>
          <textarea id="r2v_prompt" placeholder="传入多个视频时，第 1 个视频对应 character1，第 2 个对应 character2，以此类推。每个参考视频仅包含一个角色（如 character1 为小女孩，character2 为闹钟）。"></textarea>
          <div class="row">
            <div>
              <label>Size</label>
              <select id="r2v_size">
                <optgroup label="720P">
                  <option value="1280*720">1280*720（16:9）</option>
                  <option value="720*1280">720*1280（9:16）</option>
                  <option value="960*960">960*960（1:1）</option>
                  <option value="1088*832">1088*832（4:3）</option>
                  <option value="832*1088">832*1088（3:4）</option>
                </optgroup>
                <optgroup label="1080P">
                  <option value="1920*1080" selected>1920*1080（16:9）</option>
                  <option value="1080*1920">1080*1920（9:16）</option>
                  <option value="1440*1440">1440*1440（1:1）</option>
                  <option value="1632*1248">1632*1248（4:3）</option>
                  <option value="1248*1632">1248*1632（3:4）</option>
                </optgroup>
              </select>
            </div>
            <div>
              <label>Duration（仅5或10）</label>
              <select id="r2v_duration">
                <option value="5">5</option>
                <option value="10">10</option>
              </select>
            </div>
          </div>
          <div class="row">
            <div>
              <label>Model</label>
              <input id="r2v_model" value="wan2.6-r2v" />
            </div>
            <div>
              <label>Shot Type</label>
              <select id="r2v_shot_type">
                <option value="single">single</option>
                <option value="multi">multi</option>
              </select>
            </div>
          </div>
          <label>Negative Prompt（可选）</label>
          <input id="r2v_negative_prompt" value="低质量，模糊，失焦，低分辨率，噪点，压缩伪影，闪烁，抖动，画面不稳定，运动模糊，畸形，错误结构，面部变形，多余或缺失肢体，手部错误，动作不自然，僵硬动画，过曝，欠曝，光照不一致，透视错误，物体扭曲，字幕" placeholder="不希望出现的内容..." />
          <div class="checks">
            <label><input id="r2v_audio_enable" type="checkbox" checked /> audio_enable</label>
            <label><input id="r2v_watermark" type="checkbox" /> watermark</label>
          </div>
          <label>Seed（可选）</label>
          <input id="r2v_seed" type="number" min="0" max="2147483647" placeholder="留空使用随机" />
          <div class="actions">
            <button id="r2v_submit">创建任务</button>
          </div>
        </section>
          </div>
        </section>

        <section id="page_seedance" class="page" data-provider="seedance">
          <div class="grid">
            <section class="card wide">
              <h2>Seedance 1.5 pro</h2>
              <small>POST <span class="mono">/api/v1/seedance/task</span></small>
              <label>Prompt（必填）</label>
              <textarea id="sd_prompt" placeholder="描述你想生成的视频..."></textarea>
              <label>Model</label>
              <input id="sd_model" value="doubao-seedance-1-5-pro-251215" />
              <div class="row">
                <div>
                  <label>Resolution</label>
                  <select id="sd_resolution">
                    <option value="720p" selected>720p</option>
                    <option value="480p">480p</option>
                  </select>
                </div>
                <div>
                  <label>Ratio</label>
                  <select id="sd_ratio">
                    <option value="adaptive" selected>adaptive</option>
                    <option value="16:9">16:9</option>
                    <option value="9:16">9:16</option>
                    <option value="4:3">4:3</option>
                    <option value="3:4">3:4</option>
                    <option value="1:1">1:1</option>
                    <option value="21:9">21:9</option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div>
                  <label>Duration</label>
                  <select id="sd_duration">
                    <option value="-1" selected>adaptive</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                    <option value="7">7</option>
                    <option value="8">8</option>
                    <option value="9">9</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
                </div>
                <div>
                  <label>Seed（-1 或 0~4294967295）</label>
                  <input id="sd_seed" type="number" min="-1" max="4294967295" placeholder="留空使用随机" />
                </div>
              </div>
              <div class="row">
                <div>
                  <label>First Frame（可选）</label>
                  <input id="sd_first_frame" type="file" accept="image/*" />
                  <label for="sd_first_frame" class="fileBtn">选择首帧图片</label>
                  <div id="sd_first_frame_list" class="fileList"></div>
                </div>
                <div>
                  <label>Last Frame（可选）</label>
                  <input id="sd_last_frame" type="file" accept="image/*" />
                  <label id="sd_last_frame_btn" for="sd_last_frame" class="fileBtn">选择尾帧图片</label>
                  <div id="sd_last_frame_list" class="fileList"></div>
                </div>
              </div>
              <div class="checks">
                <label><input id="sd_generate_audio" type="checkbox" checked /> generate_audio</label>
                <label><input id="sd_camera_fixed" type="checkbox" /> camera_fixed</label>
                <label><input id="sd_watermark" type="checkbox" /> watermark</label>
              </div>
              <div class="actions">
                <button id="sd_submit">创建任务</button>
              </div>
            </section>
          </div>
        </section>
      </div>

      <div class="grid" style="margin-top: 14px;">
        <section id="task_section" class="wide status">
          <div class="statusTop">
            <div>
              <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <div class="muted" style="font-size:12px;">任务查询</div>
                <span id="provider_badge" class="badge">Wan2.6</span>
              </div>
              <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:8px;">
                <input id="task_id" class="mono" placeholder="task_id" style="min-width: 380px; flex: 1;" />
                <button id="query_submit" class="secondary" style="width:auto;">查询</button>
                <button id="poll_stop" class="danger" style="width:auto; display:none;">停止轮询</button>
                <span id="badge" class="badge">IDLE</span>
                <span id="cost_info" class="badge" style="display:none;"></span>
                <span id="time_info" class="badge" style="display:none;"></span>
              </div>
            </div>
            <div class="muted" style="font-size:12px;">轮询间隔：15s（SUCCEEDED/FAILED/CANCELED/UNKNOWN 自动停止）</div>
          </div>

          <div style="margin-top: 14px;">
            <div class="muted" style="font-size:12px; margin-bottom:6px;">视频预览</div>
            <video id="player" class="player" controls tabindex="0"></video>
          </div>
        </section>
      </div>
    </main>

    <script>
      const POLL_INTERVAL_MS = 15000;
      let pollTimer = null;
      let pollProvider = null;

      const $ = (id) => document.getElementById(id);

      const providers = {
        wan: {
          key: "wan",
          label: "Wan2.6",
          queryUrl: (taskId) => `/api/v1/task/${encodeURIComponent(taskId)}`,
        },
        seedance: {
          key: "seedance",
          label: "Seedance1.5pro",
          queryUrl: (taskId) => `/api/v1/seedance/task/${encodeURIComponent(taskId)}`,
        },
      };
      let activeProvider = "wan";

      const state = {
        i2vImage: null,
        i2vAudio: null,
        t2vAudio: null,
        r2vVideos: [],
        sdFirstFrame: null,
        sdLastFrame: null,
      };

      function setBadge(status) {
        const badge = $("badge");
        badge.textContent = status || "IDLE";
        badge.className = "badge";
        if (status === "SUCCEEDED") badge.classList.add("ok");
        else if (status === "FAILED" || status === "CANCELED") badge.classList.add("bad");
        else if (status === "PENDING" || status === "RUNNING") badge.classList.add("warn");
      }

      function setActiveProvider(providerKey) {
        if (!providers[providerKey]) providerKey = "wan";
        activeProvider = providerKey;

        const tabWan = $("tab_wan");
        const tabSeedance = $("tab_seedance");
        tabWan?.classList.toggle("active", providerKey === "wan");
        tabSeedance?.classList.toggle("active", providerKey === "seedance");

        const providerBadge = $("provider_badge");
        if (providerBadge) providerBadge.textContent = providers[providerKey].label;
      }

      function initProviderSwitcher() {
        const pages = $("mode_pages");
        const pageWan = $("page_wan");
        const pageSeedance = $("page_seedance");

        const scrollTo = (providerKey) => {
          if (!pages) return;
          const target = providerKey === "seedance" ? pageSeedance : pageWan;
          if (!target) return;
          pages.scrollTo({ left: target.offsetLeft, behavior: "smooth" });
        };

        $("tab_wan")?.addEventListener("click", () => {
          setActiveProvider("wan");
          scrollTo("wan");
        });
        $("tab_seedance")?.addEventListener("click", () => {
          setActiveProvider("seedance");
          scrollTo("seedance");
        });

        let scrollDebounce = null;
        pages?.addEventListener("scroll", () => {
          if (scrollDebounce) clearTimeout(scrollDebounce);
          scrollDebounce = setTimeout(() => {
            if (!pages) return;
            const idx = Math.round(pages.scrollLeft / Math.max(1, pages.clientWidth));
            setActiveProvider(idx <= 0 ? "wan" : "seedance");
          }, 80);
        });

        setActiveProvider("wan");
      }

      // 计算时间差（秒）
      function calculateDuration(startTime, endTime) {
        if (!startTime || !endTime) return null;

        try {
          const start = new Date(startTime);
          const end = new Date(endTime);

          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            return null;
          }

          // 返回秒数
          return Math.round((end - start) / 1000);
        } catch (e) {
          return null;
        }
      }

      // 格式化时间显示（秒转为易读格式）
      function formatDuration(seconds) {
        if (!seconds && seconds !== 0) return "";

        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        const parts = [];
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0) parts.push(`${minutes}m`);
        if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

        return parts.join(" ");
      }

      // 更新费用和时间显示
      function updateCostAndTimeInfo(data, providerKey) {
        const costInfo = $("cost_info");
        const timeInfo = $("time_info");

        // 重置显示
        costInfo.style.display = "none";
        timeInfo.style.display = "none";
        costInfo.textContent = "";
        timeInfo.textContent = "";

        if (!data) return;

        const key = providers[providerKey] ? providerKey : activeProvider;

        // 计算并显示费用（Seedance 不计算计费）
        if (key !== "seedance") {
          const sr = data.usage?.SR;  // 分辨率：720 或 1080
          const duration = data.usage?.output_video_duration;  // 视频时长（秒）

          if (sr && duration) {
            let pricePerSecond;
            if (sr >= 1080) {
              // 1080P: $0.15/秒
              pricePerSecond = 0.15;
            } else if (sr >= 720) {
              // 720P: $0.1/秒
              pricePerSecond = 0.1;
            } else {
              // 480P及以下不计费
              pricePerSecond = null;
            }

            if (pricePerSecond !== null) {
              const cost = pricePerSecond * duration;
              costInfo.textContent = `💰 $${cost.toFixed(2)}`;
              costInfo.style.display = "";
              costInfo.classList.add("ok");
            }
          }
        }

        // 计算并显示时间
        const submitTime = data.submit_time;
        const endTime = data.end_time;
        if (submitTime && endTime) {
          const durationSeconds = calculateDuration(submitTime, endTime);
          if (durationSeconds !== null) {
            timeInfo.textContent = `⏱️ ${formatDuration(durationSeconds)}`;
            timeInfo.style.display = "";
            timeInfo.classList.add("ok");
          }
        } else if (data?.created_at && data?.updated_at) {
          const createdAt = typeof data.created_at === "number" ? data.created_at : parseInt(String(data.created_at), 10);
          const updatedAt = typeof data.updated_at === "number" ? data.updated_at : parseInt(String(data.updated_at), 10);
          if (!isNaN(createdAt) && !isNaN(updatedAt) && updatedAt >= createdAt) {
            const durationSeconds = updatedAt - createdAt;
            timeInfo.textContent = `⏱️ ${formatDuration(durationSeconds)}`;
            timeInfo.style.display = "";
            timeInfo.classList.add("ok");
          }
        }
      }

      function setPreviewUrl(url) {
        const player = $("player");
        player.src = url || "";
      }

      function fileKey(file) {
        return `${file.name}|${file.size}|${file.lastModified}`;
      }

      function formatFilename(name, maxLen = 28) {
        if (!name || name.length <= maxLen) return name || "";
        const head = Math.ceil((maxLen - 3) * 0.65);
        const tail = Math.max(1, maxLen - 3 - head);
        return `${name.slice(0, head)}...${name.slice(-tail)}`;
      }

      function renderFileChips(containerId, files, onRemoveAtIndex) {
        const container = $(containerId);
        container.innerHTML = "";
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const chip = document.createElement("div");
          chip.className = "fileChip";

          const name = document.createElement("span");
          name.className = "fileName";
          name.title = file.name;
          name.textContent = formatFilename(file.name);

          const remove = document.createElement("button");
          remove.type = "button";
          remove.className = "fileRemove";
          remove.setAttribute("aria-label", "移除");
          remove.textContent = "×";
          remove.addEventListener("click", () => onRemoveAtIndex(i));

          chip.appendChild(name);
          chip.appendChild(remove);
          container.appendChild(chip);
        }
      }

      function renderSelectedFiles() {
        renderFileChips("t2v_audio_list", state.t2vAudio ? [state.t2vAudio] : [], () => {
          state.t2vAudio = null;
          $("t2v_audio").value = "";
          renderSelectedFiles();
        });

        renderFileChips("i2v_image_list", state.i2vImage ? [state.i2vImage] : [], () => {
          state.i2vImage = null;
          $("i2v_image").value = "";
          renderSelectedFiles();
        });

        renderFileChips("i2v_audio_list", state.i2vAudio ? [state.i2vAudio] : [], () => {
          state.i2vAudio = null;
          $("i2v_audio").value = "";
          renderSelectedFiles();
        });

        renderFileChips("r2v_video_list", state.r2vVideos, (idx) => {
          state.r2vVideos.splice(idx, 1);
          renderSelectedFiles();
        });

        renderFileChips("sd_first_frame_list", state.sdFirstFrame ? [state.sdFirstFrame] : [], () => {
          state.sdFirstFrame = null;
          state.sdLastFrame = null;
          $("sd_first_frame").value = "";
          $("sd_last_frame").value = "";
          renderSelectedFiles();
        });

        renderFileChips("sd_last_frame_list", state.sdLastFrame ? [state.sdLastFrame] : [], () => {
          state.sdLastFrame = null;
          $("sd_last_frame").value = "";
          renderSelectedFiles();
        });
      }

      async function readJsonSafely(res) {
        const text = await res.text();
        if (!text) return null;
        try { return JSON.parse(text); } catch { return { raw: text }; }
      }

      function extractErrorMessage(payload) {
        return payload?.detail?.message
          ?? payload?.detail?.error_message
          ?? payload?.message
          ?? payload?.error_message
          ?? payload?.detail
          ?? "请求失败";
      }

      function stopPolling() {
        if (pollTimer) clearTimeout(pollTimer);
        pollTimer = null;
        pollProvider = null;
        $("poll_stop").style.display = "none";
      }

      function getTaskStatus(providerKey, data) {
        if (!data) return "UNKNOWN";

        const key = providers[providerKey] ? providerKey : activeProvider;
        if (key === "seedance") {
          const raw = String(data?.status || "").toLowerCase();
          if (raw === "queued") return "PENDING";
          if (raw === "running") return "RUNNING";
          if (raw === "succeeded") return "SUCCEEDED";
          if (raw === "failed") return "FAILED";
          if (raw === "cancelled") return "CANCELED";
          return "UNKNOWN";
        }

        return data?.task_status || "UNKNOWN";
      }

      function schedulePoll(taskId, providerKey) {
        stopPolling();
        $("poll_stop").style.display = "";
        pollProvider = providers[providerKey] ? providerKey : activeProvider;
        const tick = async () => {
          try {
            const data = await queryTask(taskId, pollProvider);
            const status = getTaskStatus(pollProvider, data);
            setBadge(status);
            updateCostAndTimeInfo(data, pollProvider);
            if (["SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"].includes(status)) {
              stopPolling();
              return;
            }
          } catch (e) {
            setBadge("FAILED");
            updateCostAndTimeInfo(null);
            stopPolling();
          }
          pollTimer = setTimeout(tick, POLL_INTERVAL_MS);
        };
        pollTimer = setTimeout(tick, 0);
      }

      async function queryTask(taskId, providerKey) {
        const provider = providers[providerKey] ? providers[providerKey] : providers[activeProvider];
        const res = await fetch(provider.queryUrl(taskId));
        const payload = await readJsonSafely(res);
        if (!res.ok) {
          const msg = extractErrorMessage(payload);
          throw new Error(msg);
        }
        const data = payload?.data ?? null;
        const key = providers[providerKey] ? providerKey : activeProvider;
        const videoUrl = key === "seedance"
          ? (data?.s3_video_url ?? data?.content?.video_url ?? "")
          : (data?.s3_video_url ?? data?.video_url ?? "");
        setPreviewUrl(videoUrl);
        return data;
      }

      async function createTask(path, formData, providerKey) {
        stopPolling();
        setBadge("SUBMITTING");
        updateCostAndTimeInfo(null); // 清空之前的信息
        setPreviewUrl("");
        goToTaskSection();

        const res = await fetch(path, { method: "POST", body: formData });
        const payload = await readJsonSafely(res);
        if (!res.ok) {
          const msg = extractErrorMessage(payload);
          setBadge("FAILED");
          updateCostAndTimeInfo(null, pollProvider);
          throw new Error(msg);
        }
        if (!payload?.success) {
          const msg = payload?.message || "创建任务失败";
          setBadge("FAILED");
          updateCostAndTimeInfo(null);
          throw new Error(msg);
        }
        const key = providers[providerKey] ? providerKey : activeProvider;
        const taskId = key === "seedance" ? payload?.data?.id : payload?.data?.task_id;
        $("task_id").value = taskId || "";
        setBadge(key === "seedance" ? "PENDING" : (payload?.data?.task_status || "PENDING"));
        if (taskId) schedulePoll(taskId, providerKey);
        goToTaskSection();
        return taskId;
      }

      function appendIf(form, key, value) {
        if (value === undefined || value === null) return;
        const str = String(value).trim();
        if (!str) return;
        form.append(key, str);
      }

      function goToTaskSection() {
        const player = $("player");
        const section = $("task_section");
        const target = player || section;
        if (!target) return;
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => player?.focus(), 200);
      }

      $("i2v_image").addEventListener("change", () => {
        const file = $("i2v_image").files?.[0] || null;
        state.i2vImage = file;
        $("i2v_image").value = "";
        renderSelectedFiles();
      });

      $("t2v_audio").addEventListener("change", () => {
        const file = $("t2v_audio").files?.[0] || null;
        state.t2vAudio = file;
        $("t2v_audio").value = "";
        renderSelectedFiles();
      });

      $("i2v_audio").addEventListener("change", () => {
        const file = $("i2v_audio").files?.[0] || null;
        state.i2vAudio = file;
        $("i2v_audio").value = "";
        renderSelectedFiles();
      });

      $("r2v_videos").addEventListener("change", () => {
        const picked = Array.from($("r2v_videos").files || []);
        $("r2v_videos").value = "";
        if (picked.length === 0) return;

        const existing = new Set(state.r2vVideos.map(fileKey));
        const slots = Math.max(0, 3 - state.r2vVideos.length);
        const uniquePicked = picked.filter((f) => !existing.has(fileKey(f)));

        if (slots === 0) {
          alert("R2V: 最多 3 个参考视频");
          return;
        }

        const toAdd = uniquePicked.slice(0, slots);
        state.r2vVideos.push(...toAdd);
        renderSelectedFiles();

        const ignored = uniquePicked.length - toAdd.length;
        if (ignored > 0) alert(`R2V: 最多 3 个参考视频，已忽略 ${ignored} 个`);
      });

      $("sd_first_frame").addEventListener("change", () => {
        const file = $("sd_first_frame").files?.[0] || null;
        state.sdFirstFrame = file;
        $("sd_first_frame").value = "";
        renderSelectedFiles();
      });

      // 未选择首帧时，阻止打开尾帧选择器
      $("sd_last_frame_btn").addEventListener("click", (e) => {
        if (state.sdFirstFrame) return;
        e.preventDefault();
        e.stopPropagation();
        alert("请先选择首帧图片");
      });
      $("sd_last_frame").addEventListener("click", (e) => {
        if (state.sdFirstFrame) return;
        e.preventDefault();
        e.stopPropagation();
        alert("请先选择首帧图片");
      });

      $("sd_last_frame").addEventListener("change", () => {
        const file = $("sd_last_frame").files?.[0] || null;
        $("sd_last_frame").value = "";
        if (!file) return;
        if (!state.sdFirstFrame) {
          state.sdLastFrame = null;
          renderSelectedFiles();
          alert("请先选择首帧图片");
          return;
        }
        state.sdLastFrame = file;
        renderSelectedFiles();
      });

      // T2V
      $("t2v_submit").addEventListener("click", async (e) => {
        e.preventDefault();
        const prompt = $("t2v_prompt").value.trim();
        if (!prompt) return alert("T2V: prompt 必填");
        const form = new FormData();
        form.append("prompt", prompt);
        appendIf(form, "size", $("t2v_size").value);
        appendIf(form, "duration", $("t2v_duration").value);
        appendIf(form, "model", $("t2v_model").value);
        appendIf(form, "shot_type", $("t2v_shot_type").value);
        appendIf(form, "negative_prompt", $("t2v_negative_prompt").value);
        form.append("prompt_extend", $("t2v_prompt_extend").checked ? "true" : "false");
        form.append("audio_enable", $("t2v_audio_enable").checked ? "true" : "false");
        form.append("watermark", $("t2v_watermark").checked ? "true" : "false");
        appendIf(form, "seed", $("t2v_seed").value);
        const audioFile = state.t2vAudio;
        if (audioFile) form.append("audio", audioFile);
        try { await createTask("/api/v1/video/t2v", form, "wan"); }
        catch (e) { alert(e.message); }
      });

      // I2V
      $("i2v_submit").addEventListener("click", async (e) => {
        e.preventDefault();
        const imageFile = state.i2vImage;
        if (!imageFile) return alert("I2V: image 必填");
        const form = new FormData();
        form.append("image", imageFile);
        appendIf(form, "prompt", $("i2v_prompt").value);
        appendIf(form, "resolution", $("i2v_resolution").value);
        appendIf(form, "duration", $("i2v_duration").value);
        appendIf(form, "model", $("i2v_model").value);
        appendIf(form, "shot_type", $("i2v_shot_type").value);
        appendIf(form, "negative_prompt", $("i2v_negative_prompt").value);
        form.append("prompt_extend", $("i2v_prompt_extend").checked ? "true" : "false");
        form.append("audio_enable", $("i2v_audio_enable").checked ? "true" : "false");
        form.append("watermark", $("i2v_watermark").checked ? "true" : "false");
        appendIf(form, "seed", $("i2v_seed").value);
        const audioFile = state.i2vAudio;
        if (audioFile) form.append("audio", audioFile);
        try { await createTask("/api/v1/video/i2v", form, "wan"); }
        catch (e) { alert(e.message); }
      });

      // R2V
      $("r2v_submit").addEventListener("click", async (e) => {
        e.preventDefault();
        const files = state.r2vVideos;
        if (files.length < 1) return alert("R2V: 至少选择 1 个参考视频");
        if (files.length > 3) return alert("R2V: 最多 3 个参考视频");
        const prompt = $("r2v_prompt").value.trim();
        if (!prompt) return alert("R2V: prompt 必填");

        const form = new FormData();
        files.forEach((f) => form.append("reference_videos", f));
        form.append("prompt", prompt);
        appendIf(form, "duration", $("r2v_duration").value);
        appendIf(form, "size", $("r2v_size").value);
        appendIf(form, "model", $("r2v_model").value);
        appendIf(form, "shot_type", $("r2v_shot_type").value);
        appendIf(form, "negative_prompt", $("r2v_negative_prompt").value);
        form.append("audio_enable", $("r2v_audio_enable").checked ? "true" : "false");
        form.append("watermark", $("r2v_watermark").checked ? "true" : "false");
        appendIf(form, "seed", $("r2v_seed").value);

        try { await createTask("/api/v1/video/r2v", form, "wan"); }
        catch (e) { alert(e.message); }
      });

      // Seedance
      $("sd_submit").addEventListener("click", async (e) => {
        e.preventDefault();
        const prompt = $("sd_prompt").value.trim();
        if (!prompt) return alert("Seedance: prompt 必填");

        const firstFrame = state.sdFirstFrame;
        const lastFrame = state.sdLastFrame;
        if (lastFrame && !firstFrame) return alert("Seedance: 选择尾帧时必须同时选择首帧");

        const form = new FormData();
        appendIf(form, "model", $("sd_model").value);
        form.append("prompt", prompt);
        form.append("generate_audio", $("sd_generate_audio").checked ? "true" : "false");
        appendIf(form, "resolution", $("sd_resolution").value);
        appendIf(form, "ratio", $("sd_ratio").value);
        appendIf(form, "duration", $("sd_duration").value);
        appendIf(form, "seed", $("sd_seed").value);
        form.append("camera_fixed", $("sd_camera_fixed").checked ? "true" : "false");
        form.append("watermark", $("sd_watermark").checked ? "true" : "false");
        if (firstFrame) form.append("first_frame", firstFrame);
        if (lastFrame) form.append("last_frame", lastFrame);

        try { await createTask("/api/v1/seedance/task", form, "seedance"); }
        catch (e) { alert(e.message); }
      });

      // Query
      $("query_submit").addEventListener("click", async (e) => {
        e.preventDefault();
        stopPolling();
        const taskId = $("task_id").value.trim();
        if (!taskId) return alert("请输入 task_id");
        setBadge("QUERYING");
        updateCostAndTimeInfo(null); // 清空之前的信息
        try {
          const data = await queryTask(taskId, activeProvider);
          const status = getTaskStatus(activeProvider, data);
          setBadge(status);
          updateCostAndTimeInfo(data, activeProvider);
          if (!["SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"].includes(status)) {
            schedulePoll(taskId, activeProvider);
          }
        } catch (e) {
          setBadge("FAILED");
          updateCostAndTimeInfo(null);
          alert(e.message);
        }
      });

      $("poll_stop").addEventListener("click", (e) => {
        e.preventDefault();
        stopPolling();
        setBadge("STOPPED");
      });

      initProviderSwitcher();
      renderSelectedFiles();
    </script>
  </body>
</html>
"""
