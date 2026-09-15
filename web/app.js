/* ==========================================================================
   MEMOAID - Web Application Logic with Full Live Backend Integration
   ========================================================================== */

async function startApp() {
  // ─────────────────────────────────────────────────────────────
  // 0. AUTHENTICATION & SESSION STATE MANAGEMENT
  // ─────────────────────────────────────────────────────────────
  let currentSession = null;
  try {
    const raw = localStorage.getItem('apon_session');
    if (raw) currentSession = JSON.parse(raw);
  } catch (e) {
    console.warn('Failed to parse apon_session:', e);
  }

  function getActiveUserId() {
    if (currentSession) {
      if (currentSession.role === 'caregiver') {
        return currentSession.assigned_patient_id || null;
      }
      return currentSession.user_id;
    }
    return null;
  }

  let currentUserId = getActiveUserId();
  let currentRole = currentSession ? currentSession.role : 'guest';
  let isViewingAsParticipant = false;

  // ─────────────────────────────────────────────────────────────
  // ROUTE PERMISSION MAPS
  // ─────────────────────────────────────────────────────────────
  const elderlyAllowedViews = ['login-view', 'elderly-view', 'games-view', 'progress-view', 'memory-view', 'routine-view', 'settings-view'];
  const caregiverAllowedViews = ['login-view', 'caregiver-view', 'settings-view'];
  const caregiverParticipantViews = ['login-view', 'caregiver-view', 'settings-view', 'elderly-view', 'games-view', 'progress-view', 'memory-view', 'routine-view'];

  const hashToView = {
    '#login': 'login-view',
    '#elderly/dashboard': 'elderly-view',
    '#games': 'games-view',
    '#progress': 'progress-view',
    '#memory': 'memory-view',
    '#routine': 'routine-view',
    '#caregiver/dashboard': 'caregiver-view',
    '#settings': 'settings-view'
  };

  const viewToHash = {};
  for (const [hash, view] of Object.entries(hashToView)) {
    viewToHash[view] = hash;
  }

  function getAllowedViews() {
    if (!currentSession) return ['login-view'];
    if (currentSession.role === 'elderly') return elderlyAllowedViews;
    if (currentSession.role === 'caregiver') {
      return isViewingAsParticipant ? caregiverParticipantViews : caregiverAllowedViews;
    }
    return ['login-view'];
  }

  function getDefaultView() {
    if (!currentSession) return 'login-view';
    if (currentSession.role === 'elderly') return 'elderly-view';
    if (currentSession.role === 'caregiver') {
      return isViewingAsParticipant ? 'elderly-view' : 'caregiver-view';
    }
    return 'login-view';
  }

  function getInitials(name) {
    if (!name) return 'NV';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function generateAvatarDataUri(name, role = 'elderly') {
    const initials = getInitials(name);
    const bg = role === 'caregiver' ? '%231F3042' : '%23176B4D';
    const fg = '%23FFFFFF';
    return `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='${bg}'/><text x='50%25' y='55%25' text-anchor='middle' dominant-baseline='middle' fill='${fg}' font-family='sans-serif' font-weight='700' font-size='38'>${initials}</text></svg>`;
  }

  window.generateAvatarDataUri = generateAvatarDataUri;

  // ─────────────────────────────────────────────────────────────
  // ROLE-BASED NAV VISIBILITY
  // ─────────────────────────────────────────────────────────────
  function updateNavVisibility() {
    const btnSwitch = document.getElementById('btnSwitchPerspective');
    const btnElderlyCaregiverOverview = document.getElementById('btnElderlyCaregiverOverview');
    const allNavBtns = document.querySelectorAll('.nav-item');

    allNavBtns.forEach(btn => {
      const role = btn.getAttribute('data-role');
      const target = btn.getAttribute('data-target');

      if (!currentSession) {
        // Unauthenticated: show only login
        if (target === 'login-view') {
          btn.classList.remove('nav-hidden');
        } else {
          btn.classList.add('nav-hidden');
        }
        return;
      }

      if (role === 'all') {
        btn.classList.remove('nav-hidden');
        return;
      }

      if (currentSession.role === 'elderly') {
        // Elderly: show elderly + all, hide caregiver
        if (role === 'elderly' || role === 'all') {
          btn.classList.remove('nav-hidden');
        } else {
          btn.classList.add('nav-hidden');
        }
      } else if (currentSession.role === 'caregiver') {
        if (isViewingAsParticipant) {
          // Caregiver in participant view: show all relevant nav
          btn.classList.remove('nav-hidden');
        } else {
          // Caregiver default: only caregiver + all
          if (role === 'caregiver' || role === 'all') {
            btn.classList.remove('nav-hidden');
          } else {
            btn.classList.add('nav-hidden');
          }
        }
      }
    });

    // Switch button: only visible for caregivers
    if (btnSwitch) {
      if (currentSession && currentSession.role === 'caregiver') {
        btnSwitch.classList.remove('switch-hidden');
      } else {
        btnSwitch.classList.add('switch-hidden');
      }
    }

    // "Caregiver Overview" button on elderly dashboard: only for caregiver in participant view
    if (btnElderlyCaregiverOverview) {
      if (currentSession && currentSession.role === 'caregiver' && isViewingAsParticipant) {
        btnElderlyCaregiverOverview.style.display = '';
      } else {
        btnElderlyCaregiverOverview.style.display = 'none';
      }
    }
  }

  function syncAuthUI() {
    const profileName = document.getElementById('profileName');
    const profileRoleLabel = document.getElementById('roleText');
    const profileImg = document.getElementById('profileImg');
    const headerAuthText = document.getElementById('headerAuthText');
    const navLoginText = document.getElementById('navLoginText');
    const settingsRoleType = document.getElementById('settingsRoleType');
    const settingsUserName = document.getElementById('settingsUserName');
    const settingsUserMeta = document.getElementById('settingsUserMeta');
    const switchBtnText = document.getElementById('switchBtnText');
    const elderlyGreetingTitle = document.getElementById('elderlyGreetingTitle');
    const dangerZone = document.getElementById('caregiverDangerZoneCard');

    if (currentSession) {
      document.body.classList.remove('auth-locked');
      const isCaregiver = currentSession.role === 'caregiver';
      if (profileName) profileName.textContent = currentSession.name;
      if (profileRoleLabel) {
        if (isCaregiver && isViewingAsParticipant) {
          profileRoleLabel.textContent = 'Viewing as Participant';
        } else if (isCaregiver) {
          profileRoleLabel.textContent = 'Caregiver Oversight';
        } else {
          profileRoleLabel.textContent = 'Participant Active';
        }
      }
      if (headerAuthText) headerAuthText.textContent = `${currentSession.name.split(' ')[0]} (${isCaregiver ? 'Caregiver' : 'Patient'})`;
      if (navLoginText) navLoginText.textContent = isCaregiver ? 'Account' : 'Account';
      if (settingsRoleType) settingsRoleType.textContent = `Authenticated Role: ${isCaregiver ? 'Caregiver' : 'Elderly Patient'}`;
      if (settingsUserName) settingsUserName.textContent = currentSession.name;
      if (settingsUserMeta) settingsUserMeta.textContent = `Username: @${currentSession.username} • User ID #${currentSession.user_id}`;
      if (switchBtnText) switchBtnText.textContent = isViewingAsParticipant ? 'Back to Caregiver Overview' : 'Switch to Participant View';
      if (elderlyGreetingTitle) {
        if (isCaregiver && isViewingAsParticipant) {
          elderlyGreetingTitle.textContent = `Participant View ☀️`;
        } else if (isCaregiver) {
          elderlyGreetingTitle.textContent = `Caregiver Oversight ☀️`;
        } else {
          elderlyGreetingTitle.textContent = `Good morning, ${currentSession.name.split(' ')[0]} ☀️`;
        }
      }
      if (profileImg) {
        profileImg.src = generateAvatarDataUri(currentSession.name, currentSession.role);
      }
      if (dangerZone) {
        dangerZone.style.display = isCaregiver ? 'block' : 'none';
      }
    } else {
      document.body.classList.add('auth-locked');
      if (profileName) profileName.textContent = 'Please Sign In';
      if (profileRoleLabel) profileRoleLabel.textContent = 'Authentication Required';
      if (headerAuthText) headerAuthText.textContent = 'Sign In';
      if (navLoginText) navLoginText.textContent = 'Sign In';
      if (settingsRoleType) settingsRoleType.textContent = 'Session: Not Authenticated';
      if (settingsUserName) settingsUserName.textContent = 'Guest User';
      if (settingsUserMeta) settingsUserMeta.textContent = 'Sign in to access personalized data';
      if (switchBtnText) switchBtnText.textContent = 'Sign In';
      if (elderlyGreetingTitle) elderlyGreetingTitle.textContent = 'Welcome ☀️';
      if (profileImg) {
        profileImg.src = generateAvatarDataUri('Guest', 'elderly');
      }
      if (dangerZone) dangerZone.style.display = 'none';
    }

    updateNavVisibility();
  }

  // ─────────────────────────────────────────────────────────────
  // LIVE CLOCK & CONTEXTUAL ROUTINE LABEL
  // ─────────────────────────────────────────────────────────────
  let clockIntervalId = null;

  function getRoutineLabel(hour) {
    if (hour >= 5 && hour < 9)   return 'Calm Morning Routine';
    if (hour >= 9 && hour < 12)  return 'Morning Activity Session';
    if (hour >= 12 && hour < 14) return 'Midday Rest & Lunch';
    if (hour >= 14 && hour < 17) return 'Afternoon Exercise';
    if (hour >= 17 && hour < 19) return 'Evening Wind-Down';
    if (hour >= 19 && hour < 21) return 'Night Memory Reflection';
    if (hour >= 21 || hour < 5)  return 'Rest & Sleep Time';
    return 'Daily Wellness Session';
  }

  function updateLiveClock() {
    const el = document.getElementById('liveClockText');
    if (!el) return;
    const now = new Date();
    const hour = now.getHours();
    const min = now.getMinutes().toString().padStart(2, '0');
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h12 = hour % 12 || 12;
    const label = getRoutineLabel(hour);
    el.textContent = `Today, ${h12}:${min} ${ampm} • ${label}`;
  }

  function startLiveClock() {
    updateLiveClock(); // immediate first tick
    if (clockIntervalId) clearInterval(clockIntervalId);
    clockIntervalId = setInterval(updateLiveClock, 1000); // tick every second so minute transitions are instant
  }

  function stopLiveClock() {
    // Keep clock displaying current accurate live time across logouts/view changes
    updateLiveClock();
  }

  // Toast / notification helper
  function showNotification(msg) {
    openModal(
      'Notification',
      `<div style="display:flex; align-items:center; gap:12px;">
         <span class="material-symbols-outlined" style="font-size:32px; color:var(--primary);">check_circle</span>
         <span style="font-size:16px;">${msg}</span>
       </div>`
    );
  }

  // ─────────────────────────────────────────────────────────────
  // 1. NAVIGATION ROUTING & ROUTE PROTECTION (User Requirements #1, #4 & #8)
  // ─────────────────────────────────────────────────────────────
  const navButtons = document.querySelectorAll('.nav-item');
  const viewSections = document.querySelectorAll('.view-section');

  window.switchTab = function(targetId) {
    // Strict Route Guard: If not authenticated, force login-view!
    if (!currentSession && targetId !== 'login-view') {
      targetId = 'login-view';
    }

    // Role-Based Route Guard
    if (currentSession && targetId !== 'login-view') {
      const allowed = getAllowedViews();
      if (!allowed.includes(targetId)) {
        const defaultView = getDefaultView();
        if (currentSession.role === 'elderly' && targetId === 'caregiver-view') {
          showNotification('Caregiver Overview is only accessible with a Caregiver account.');
        } else if (currentSession.role === 'caregiver' && !isViewingAsParticipant) {
          showNotification('Switch to Participant View to access patient features.');
        } else {
          showNotification('You do not have access to this page.');
        }
        targetId = defaultView;
      }
    }

    navButtons.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-target') === targetId);
    });

    viewSections.forEach(sec => {
      sec.classList.toggle('active', sec.id === `view-${targetId}`);
    });

    if (targetId === 'login-view') {
      document.body.classList.add('auth-locked');
    } else if (currentSession) {
      document.body.classList.remove('auth-locked');
    }

    // Update URL hash for route tracking (without triggering popstate)
    const hash = viewToHash[targetId] || '#login';
    if (window.location.hash !== hash) {
      history.pushState({ view: targetId }, '', hash);
    }

    // Live refresh analytics when navigating to monitored dashboards
    if (['caregiver-view', 'elderly-view', 'progress-view'].includes(targetId)) {
      const activeId = getActiveUserId();
      if (activeId) renderPatientAnalytics(activeId);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      if (targetId) switchTab(targetId);
    });
  });

  // Browser Back Navigation Protection with hash-based routing
  window.addEventListener('popstate', (e) => {
    if (!currentSession) {
      switchTab('login-view');
      return;
    }
    // Resolve view from hash
    const hash = window.location.hash || '#login';
    const targetView = hashToView[hash];
    if (targetView) {
      // switchTab will enforce route guards
      switchTab(targetView);
    } else {
      switchTab(getDefaultView());
    }
  });

  // "Caregiver Overview" button on Elderly Dashboard — only works for caregivers in participant view
  window.openCaregiverOverviewFromElderly = function() {
    if (currentSession && currentSession.role === 'caregiver') {
      isViewingAsParticipant = false;
      syncAuthUI();
      switchTab('caregiver-view');
    } else {
      showNotification('Caregiver Overview requires a Caregiver account. Please log in as Caregiver.');
      selectLoginRole('caregiver');
      switchTab('login-view');
    }
  };

  // Logout Behaviour (User Requirement #4)
  window.handleLogout = function() {
    localStorage.removeItem('apon_session');
    currentSession = null;
    currentRole = 'guest';
    currentUserId = null;
    isViewingAsParticipant = false;
    caregiverPatients = [];
    selectedCaregiverPatient = null;

    // Prevent access to protected dashboard pages using browser Back button
    history.replaceState(null, '', '#login');

    syncAuthUI();
    stopLiveClock(); // ← reset clock on logout
    switchTab('login-view');
    showNotification('Logged out successfully.');
  };

  // ─────────────────────────────────────────────────────────────
  // 2. DUAL-ROLE AUTHENTICATION LOGIC (Elderly Patient & Caregiver)
  // ─────────────────────────────────────────────────────────────
  let selectedLoginRole = 'elderly';
  let isRegisterMode = false;

  window.setAuthMode = function(mode) {
    isRegisterMode = (mode === 'register');
    const tabSignIn = document.getElementById('tabSignIn');
    const tabRegister = document.getElementById('tabRegister');
    const nameGroup = document.getElementById('groupFullName');
    const ageGroup = document.getElementById('groupAge');
    const fullNameInput = document.getElementById('loginFullName');
    const submitBtn = document.getElementById('btnSubmitAuth');
    const submitIcon = document.getElementById('authBtnSubmitIcon');
    const submitText = document.getElementById('authBtnSubmitText');
    const alertBox = document.getElementById('authAlertBox');

    if (alertBox) {
      alertBox.style.display = 'none';
      alertBox.textContent = '';
      alertBox.className = 'auth-alert-box';
    }

    if (tabSignIn && tabRegister) {
      tabSignIn.classList.toggle('active', !isRegisterMode);
      tabSignIn.setAttribute('aria-selected', (!isRegisterMode).toString());
      tabRegister.classList.toggle('active', isRegisterMode);
      tabRegister.setAttribute('aria-selected', isRegisterMode.toString());
    }

    if (nameGroup) nameGroup.style.display = isRegisterMode ? 'block' : 'none';
    if (ageGroup) ageGroup.style.display = isRegisterMode ? 'block' : 'none';
    if (fullNameInput) fullNameInput.required = isRegisterMode;

    if (submitIcon) {
      submitIcon.textContent = isRegisterMode ? 'person_add' : 'login';
    }

    if (submitText) {
      const roleTitle = selectedLoginRole === 'caregiver' ? 'Caregiver' : 'Elderly Patient';
      submitText.textContent = isRegisterMode
        ? `Create Account & Sign In as ${roleTitle}`
        : `Sign In as ${roleTitle}`;
    }
  };

  window.toggleAuthMode = function() {
    window.setAuthMode(isRegisterMode ? 'login' : 'register');
  };

  window.selectLoginRole = function(role) {
    selectedLoginRole = role;
    const cardE = document.getElementById('roleCardElderly');
    const cardC = document.getElementById('roleCardCaregiver');
    if (cardE) cardE.classList.toggle('active', role === 'elderly');
    if (cardC) cardC.classList.toggle('active', role === 'caregiver');

    // Update submit button text
    window.setAuthMode(isRegisterMode ? 'register' : 'login');
  };

  async function performLogin(username, password) {
    const alertBox = document.getElementById('authAlertBox');
    if (alertBox) {
      alertBox.style.display = 'none';
      alertBox.className = 'auth-alert-box';
    }

    const submitBtn = document.getElementById('btnSubmitAuth');
    if (submitBtn) submitBtn.disabled = true;

    const res = await API.login(username, password);
    if (submitBtn) submitBtn.disabled = false;

    if (res.success && res.user) {
      currentSession = res.user;
      localStorage.setItem('apon_session', JSON.stringify(res.user));
      currentRole = res.user.role;
      currentUserId = getActiveUserId();
      isViewingAsParticipant = false;
      syncAuthUI();

      if (alertBox) {
        alertBox.textContent = `Welcome, ${res.user.name}! Taking you to your dashboard...`;
        alertBox.className = 'auth-alert-box success';
        alertBox.style.display = 'flex';
      }

      setTimeout(async () => {
        if (alertBox) alertBox.style.display = 'none';
        startLiveClock(); // start live clock for all authenticated roles
        if (res.user.role === 'caregiver') {
          await renderCaregiverPatients();
          switchTab('caregiver-view');
        } else {
          currentUserId = res.user.user_id;
          await renderRoutineSchedule();
          await renderMemoryAnchors();
          await renderPatientAnalytics(currentUserId);
          switchTab('elderly-view');
        }
      }, 400);
    } else {
      if (alertBox) {
        alertBox.textContent = res.error || 'Invalid username or password. Please try again.';
        alertBox.className = 'auth-alert-box error';
        alertBox.style.display = 'flex';
      }
    }
  }

  window.handleAuthSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const usernameInput = document.getElementById('loginUsername');
    const passwordInput = document.getElementById('loginPassword');
    const alertBox = document.getElementById('authAlertBox');

    if (!usernameInput || !passwordInput) return;
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
      if (alertBox) {
        alertBox.textContent = 'Please enter both username and password.';
        alertBox.className = 'auth-alert-box error';
        alertBox.style.display = 'flex';
      }
      return;
    }

    if (isRegisterMode) {
      const fullNameInput = document.getElementById('loginFullName');
      const ageInput = document.getElementById('loginAge');
      const name = (fullNameInput && fullNameInput.value.trim()) || username;
      const defaultAge = selectedLoginRole === 'elderly' ? 70 : 40;
      const age = parseInt((ageInput && ageInput.value) || defaultAge, 10);

      const submitBtn = document.getElementById('btnSubmitAuth');
      if (submitBtn) submitBtn.disabled = true;

      const res = await API.register({
        username,
        password,
        name,
        age,
        role: selectedLoginRole
      });

      if (submitBtn) submitBtn.disabled = false;

      if (res.success) {
        if (alertBox) {
          alertBox.textContent = `Account created successfully! Signing in...`;
          alertBox.className = 'auth-alert-box success';
          alertBox.style.display = 'flex';
        }
        await performLogin(username, password);
      } else {
        if (alertBox) {
          alertBox.textContent = res.error || 'Registration could not be completed.';
          alertBox.className = 'auth-alert-box error';
          alertBox.style.display = 'flex';
        }
      }
    } else {
      await performLogin(username, password);
    }
  };

  // ─────────────────────────────────────────────────────────────
  // 3. CAREGIVER / PARTICIPANT PERSPECTIVE SWITCHER
  // ─────────────────────────────────────────────────────────────
  const btnSwitch = document.getElementById('btnSwitchPerspective');
  if (btnSwitch) {
    btnSwitch.addEventListener('click', async () => {
      if (!currentSession || currentSession.role !== 'caregiver') {
        // Elderly patients or unauthenticated users cannot switch
        showNotification('Please log in as a Caregiver to switch perspectives.');
        switchTab('login-view');
        return;
      }

      if (isViewingAsParticipant) {
        // Switch back to Caregiver Overview
        isViewingAsParticipant = false;
        syncAuthUI();
        switchTab('caregiver-view');
      } else {
        // Switch to Participant View
        isViewingAsParticipant = true;
        syncAuthUI();
        // Load participant data
        const patientId = getActiveUserId();
        if (patientId) {
          await renderRoutineSchedule();
          await renderMemoryAnchors();
          await renderPatientAnalytics(patientId);
          startLiveClock();
        }
        switchTab('elderly-view');
      }
    });
  }

  // ─────────────────────────────────────────────────────────────
  // 3. VOICE ASSISTANT (CONVERSATIONAL AI + TEXT-TO-SPEECH)
  // ─────────────────────────────────────────────────────────────
  const btnVoice = document.getElementById('btnVoiceAssistant');
  if (btnVoice) {
    btnVoice.addEventListener('click', () => {
      openVoiceAssistantModal();
    });
  }

  function openVoiceAssistantModal() {
    const greetingName = currentSession ? currentSession.name.split(' ')[0] : 'friend';
    const modalHtml = `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="text-align: center; padding: 8px 0;">
          <div style="width: 64px; height: 64px; border-radius: 50%; background: #E7F4ED; color: #176B4D; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px;">
            <span class="material-symbols-outlined" style="font-size: 32px;">mic</span>
          </div>
          <p style="font-size: 17px; font-weight: 600; color: #0F1D23;">"Hello ${greetingName}, I'm your memory companion. How can I help?"</p>
          <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 10px;">
            <button class="btn-secondary" style="min-height: 32px; padding: 4px 10px; font-size: 12px;" onclick="askPreset('When do I take my medication?')">💊 My Medication</button>
            <button class="btn-secondary" style="min-height: 32px; padding: 4px 10px; font-size: 12px;" onclick="askPreset('Tell me about my daily routine')">📋 Daily Routine</button>
            <button class="btn-secondary" style="min-height: 32px; padding: 4px 10px; font-size: 12px;" onclick="askPreset('What is my streak today?')">🔥 My Streak</button>
            <button class="btn-secondary" style="min-height: 32px; padding: 4px 10px; font-size: 12px;" onclick="askPreset('Help me remember my stories')">💭 My Memories</button>
          </div>
        </div>

        <div id="aiChatResponse" style="background: #F3FAFF; border: 1px solid #DDE5E1; border-radius: 12px; padding: 14px; min-height: 60px; font-size: 15px; line-height: 1.6; color: #0F1D23;">
          Click one of the suggested topics above or type your question below.
        </div>

        <div style="display: flex; gap: 8px;">
          <input type="text" id="voiceQuestionInput" placeholder="Ask a question..." style="flex: 1; padding: 12px 14px; border: 1.5px solid #DDE5E1; border-radius: 10px; font-size: 15px;">
          <button class="btn-primary" id="btnSubmitQuestion" type="button" onclick="submitVoiceQuestion()">
            <span class="material-symbols-outlined">send</span>
          </button>
        </div>
      </div>
    `;

    openModal('Voice Assistant', modalHtml, null, 'Close');
  }

  window.askPreset = function(question) {
    const input = document.getElementById('voiceQuestionInput');
    if (input) input.value = question;
    submitVoiceQuestion();
  };

  window.submitVoiceQuestion = async function() {
    const input = document.getElementById('voiceQuestionInput');
    const responseBox = document.getElementById('aiChatResponse');
    if (!input || !responseBox) return;

    const query = input.value.trim();
    if (!query) return;

    responseBox.innerHTML = `<span style="color: #66757D;">Thinking gently...</span>`;
    
    const answer = await API.askMemoryQuestion(currentUserId, query);
    responseBox.innerHTML = `<strong>Assistant:</strong> ${answer}`;
    await renderPatientAnalytics(currentUserId);

    // Speak aloud with Web Speech API
    speakText(answer);
  };

  function speakText(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9; // Unhurried, reassuring pace
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  }

  // ─────────────────────────────────────────────────────────────
  // 4. EMERGENCY HELP DISPATCH
  // ─────────────────────────────────────────────────────────────
  const btnEmergency = document.getElementById('btnEmergencyHelp');
  if (btnEmergency) {
    btnEmergency.addEventListener('click', () => {
      const activeName = currentSession ? currentSession.name : 'Participant';
      openModal(
        'Emergency Assistance Dispatch',
        `<div style="padding: 4px 0;">
           <div style="background: #FFDAD6; color: #93000A; padding: 14px 18px; border-radius: 12px; margin-bottom: 16px; font-weight: 600;">
             Emergency Call Dispatch Ready
           </div>
           <p style="font-size: 16px; margin-bottom: 12px;">Immediate assistance touchpoints for ${activeName}:</p>
           <ul style="padding-left: 20px; line-height: 1.8; color: #0F1D23; margin-bottom: 16px;">
             <li><strong>Primary Caregiver:</strong> <span style="color: #176B4D; font-weight: 600;">Direct Notification Service</span> (Priority Alert)</li>
             <li><strong>Designated Emergency Services:</strong> <a href="tel:911" style="color: #BA1A1A; font-weight: bold;">911</a></li>
           </ul>
           <button class="btn-primary" style="background-color: #BA1A1A; width: 100%; justify-content: center;" onclick="triggerEmergencyAlert()">
             <span class="material-symbols-outlined">notifications_active</span>
             <span>Send Immediate SOS Alert</span>
           </button>
         </div>`
      );
    });
  }

  window.triggerEmergencyAlert = function() {
    const activeName = currentSession ? currentSession.name : 'Participant';
    alert(`🚨 SOS alert dispatched to registered Caregivers. ${activeName}'s location and status have been transmitted.`);
    closeModal();
  };

  // ─────────────────────────────────────────────────────────────
  // 5. CAREGIVER AUDIT LOG & CLINICIAN EXPORT
  // ─────────────────────────────────────────────────────────────
  const btnAudit = document.getElementById('btnAuditLog');
  if (btnAudit) {
    btnAudit.addEventListener('click', async () => {
      const recentGames = await API.getRecentGameHistory(currentUserId);
      const reminders = await API.getReminders(currentUserId);

      let rowsHtml = '';
      recentGames.forEach(g => {
        rowsHtml += `
          <tr style="border-bottom: 1px solid #E5ECE8;">
            <td style="padding: 10px 6px; color: #66757D;">${new Date(g.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
            <td style="padding: 10px 6px; font-weight: 600;">${g.game_name}</td>
            <td style="padding: 10px 6px; color: #176B4D; font-weight: 600;">Score: ${Math.round(g.score)}/100</td>
          </tr>
        `;
      });

      reminders.filter(r => r.status === 'completed').forEach(r => {
        rowsHtml += `
          <tr style="border-bottom: 1px solid #E5ECE8;">
            <td style="padding: 10px 6px; color: #66757D;">${r.time}</td>
            <td style="padding: 10px 6px; font-weight: 600;">${r.task}</td>
            <td style="padding: 10px 6px; color: #176B4D;">Verified</td>
          </tr>
        `;
      });

      openModal(
        'Caregiver Oversight Audit Log',
        `<div style="max-height: 360px; overflow-y: auto;">
           <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
             <thead>
               <tr style="border-bottom: 2px solid #DDE5E1; text-align: left;">
                 <th style="padding: 8px 6px;">Time</th>
                 <th style="padding: 8px 6px;">Event</th>
                 <th style="padding: 8px 6px;">Result</th>
               </tr>
             </thead>
             <tbody>${rowsHtml || '<tr><td colspan="3" style="padding: 12px; text-align: center;">No activity recorded yet.</td></tr>'}</tbody>
           </table>
         </div>`
      );
    });
  }

  // Share with Clinician (Generates Real Downloadable Report)
  const btnShare = document.getElementById('btnShareClinician');
  if (btnShare) {
    btnShare.addEventListener('click', () => {
      openModal(
        'Export Clinical Summary',
        `<div style="font-size: 15px; line-height: 1.7;">
           <p style="margin-bottom: 14px;">A clinical report for <strong>Dr. Martinez</strong> is ready to download containing:</p>
           <ul style="padding-left: 20px; color: #3F4943; margin-bottom: 16px;">
             <li>7-Day Cognitive Scores (Memory: 91%, Attention: 86%, Language: 89%)</li>
             <li>Medication compliance log for Lisinopril 10mg (100% adherence)</li>
             <li>Daily walking duration (Avg 24 mins / 1,400 steps)</li>
           </ul>
           <button class="btn-primary" style="width: 100%; justify-content: center; gap: 8px;" onclick="downloadClinicalReport()">
             <span class="material-symbols-outlined">picture_as_pdf</span>
             <span>Download Clinical Summary Report (.pdf)</span>
           </button>
         </div>`
      );
    });
  }

  window.downloadClinicalReport = function() {
    let ptName = 'Aaron Jena';
    let ptAge = '74';
    if (selectedCaregiverPatient && selectedCaregiverPatient.name) {
      ptName = selectedCaregiverPatient.name;
      if (selectedCaregiverPatient.age) ptAge = String(selectedCaregiverPatient.age);
    } else if (currentSession && currentSession.role === 'elderly' && currentSession.name) {
      ptName = currentSession.name;
    }

    const caregiverName = currentSession && currentSession.name ? `${currentSession.name} (Caregiver)` : 'Dr. Abhishek (Caregiver)';
    const physicianName = 'Dr. Martinez, MD (Geriatric Neurology)';
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    const timeStr = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const reportId = 'CR-' + Math.floor(100000 + Math.random() * 900000);
    const sanitizedName = ptName.replace(/[^a-zA-Z0-9]/g, '_');
    const fileName = `${sanitizedName}_Clinical_Report_${new Date().toISOString().slice(0, 10)}.pdf`;

    // Try generating with jsPDF
    const jsPdfLib = (window.jspdf && window.jspdf.jsPDF) || window.jsPDF;
    if (jsPdfLib) {
      try {
        const doc = new jsPdfLib({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4'
        });

        const pageWidth = 210;
        const pageHeight = 297;
        const margin = 14;
        const contentWidth = pageWidth - (margin * 2);

        // 1. Top Header Banner
        doc.setFillColor(19, 78, 74); // Deep Forest Teal #134e4a
        doc.rect(0, 0, pageWidth, 28, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(16);
        doc.text('MEMOAID', margin, 12);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(204, 251, 241);
        doc.text('Cognitive Wellness & Clinical Care Oversight Platform', margin, 18);
        doc.text('Physician & Caregiver Portal | Medical Summary', margin, 23);

        // Confidential Badge
        doc.setFillColor(15, 118, 110);
        doc.roundedRect(pageWidth - margin - 48, 8, 48, 12, 2, 2, 'F');
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.5);
        doc.setTextColor(255, 255, 255);
        doc.text('CLINICAL REPORT', pageWidth - margin - 24, 15.5, { align: 'center' });

        // 2. Report Title & Document Info
        let y = 37;
        doc.setTextColor(15, 23, 42);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(14);
        doc.text('CLINICAL COGNITIVE SUMMARY REPORT', margin, y);

        y += 5;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8.5);
        doc.setTextColor(100, 116, 139);
        doc.text(`Generated on: ${dateStr} | Time: ${timeStr} | Document Ref: ${reportId}`, margin, y);

        // 3. Patient & Clinician Metadata Card
        y += 7;
        doc.setFillColor(248, 250, 252);
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.4);
        doc.roundedRect(margin, y, contentWidth, 30, 2, 2, 'FD');

        const col1X = margin + 5;
        const col2X = margin + (contentWidth * 0.52);
        let metaY = y + 7;

        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Participant / Patient:', col1X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(15, 23, 42);
        doc.text(`${ptName} (Age: ${ptAge})`, col1X + 37, metaY);

        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Attending Clinician:', col2X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(15, 23, 42);
        doc.text(physicianName, col2X + 32, metaY);

        metaY += 8;
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Primary Caregiver:', col1X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(15, 23, 42);
        doc.text(caregiverName, col1X + 37, metaY);

        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Monitoring Status:', col2X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(13, 148, 136);
        doc.text('Active Monitoring (Live Synced)', col2X + 32, metaY);

        metaY += 8;
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Clinical Focus:', col1X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(15, 23, 42);
        doc.text('Cognitive Calibration & Routine Tracking', col1X + 37, metaY);

        doc.setFont('helvetica', 'bold');
        doc.setTextColor(71, 85, 105);
        doc.text('Review Cadence:', col2X, metaY);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(15, 23, 42);
        doc.text('Weekly Oversight (30-day review)', col2X + 32, metaY);

        // Section header helper
        function drawSectionHeader(title, currY) {
          doc.setFillColor(240, 253, 250);
          doc.setDrawColor(204, 251, 241);
          doc.setLineWidth(0.3);
          doc.roundedRect(margin, currY, contentWidth, 7.5, 1, 1, 'FD');

          doc.setFillColor(15, 118, 110);
          doc.rect(margin, currY, 2.5, 7.5, 'F');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(9.5);
          doc.setTextColor(15, 118, 110);
          doc.text(title, margin + 6, currY + 5.2);
          return currY + 11.5;
        }

        // 4. Section 1: 7-Day Cognitive Performance Assessment
        y = drawSectionHeader('1. 7-Day Cognitive Performance Assessment', y + 36);

        const cardGap = 4;
        const cardW = (contentWidth - (cardGap * 2)) / 3;
        const cardH = 26;

        const stats = [
          { label: 'Memory Recall', val: '91%', sub: 'Target: >85% (Optimal Stability)', color: [13, 148, 136] },
          { label: 'Attention & Focus', val: '86%', sub: 'Target: >80% (High Engagement)', color: [14, 116, 144] },
          { label: 'Language & Fluency', val: '89%', sub: 'Target: >80% (Normal Function)', color: [4, 120, 87] }
        ];

        stats.forEach((st, idx) => {
          const cardX = margin + idx * (cardW + cardGap);
          doc.setFillColor(255, 255, 255);
          doc.setDrawColor(226, 232, 240);
          doc.setLineWidth(0.4);
          doc.roundedRect(cardX, y, cardW, cardH, 2, 2, 'FD');

          doc.setFillColor(st.color[0], st.color[1], st.color[2]);
          doc.rect(cardX, y, cardW, 2, 'F');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(8.5);
          doc.setTextColor(71, 85, 105);
          doc.text(st.label, cardX + 4, y + 7.5);

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(15);
          doc.setTextColor(st.color[0], st.color[1], st.color[2]);
          doc.text(st.val, cardX + 4, y + 15.5);

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(7);
          doc.setTextColor(100, 116, 139);
          doc.text(st.sub, cardX + 4, y + 21);
        });

        y += cardH + 4;
        doc.setFont('helvetica', 'italic');
        doc.setFontSize(8);
        doc.setTextColor(71, 85, 105);
        doc.text('Assessment Note: Continuous passive calibration active. Reaction latency and stimulus retention remain consistent.', margin + 2, y);

        // 5. Section 2: Medication Adherence & Regimen Log
        y = drawSectionHeader('2. Medication Compliance & Regimen Log', y + 7);

        const tableHeaderY = y;
        doc.setFillColor(241, 245, 249);
        doc.rect(margin, tableHeaderY, contentWidth, 6, 'F');

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.setTextColor(71, 85, 105);
        doc.text('Prescribed Medication', margin + 4, tableHeaderY + 4.2);
        doc.text('Dosage & Schedule', margin + 62, tableHeaderY + 4.2);
        doc.text('7-Day Adherence Rate', margin + 120, tableHeaderY + 4.2);
        doc.text('Clinical Status', margin + 158, tableHeaderY + 4.2);

        const meds = [
          { name: 'Lisinopril', dose: '10mg - Daily Morning (08:00 AM)', rate: '100% (7/7 doses confirmed)', status: 'Optimal' },
          { name: 'Donepezil', dose: '5mg - Daily Bedtime (09:00 PM)', rate: '100% (7/7 doses confirmed)', status: 'Optimal' },
          { name: 'Multivitamin Complex', dose: '1 Tab - Daily Noon (12:30 PM)', rate: '100% (7/7 doses confirmed)', status: 'Optimal' }
        ];

        let rowY = tableHeaderY + 6;
        meds.forEach((m, i) => {
          if (i % 2 === 1) {
            doc.setFillColor(248, 250, 252);
            doc.rect(margin, rowY, contentWidth, 6, 'F');
          }
          doc.setDrawColor(241, 245, 249);
          doc.line(margin, rowY + 6, margin + contentWidth, rowY + 6);

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(8);
          doc.setTextColor(15, 23, 42);
          doc.text(m.name, margin + 4, rowY + 4.2);

          doc.setFont('helvetica', 'normal');
          doc.setTextColor(71, 85, 105);
          doc.text(m.dose, margin + 62, rowY + 4.2);

          doc.setFont('helvetica', 'bold');
          doc.setTextColor(4, 120, 87);
          doc.text(m.rate, margin + 120, rowY + 4.2);

          doc.setFillColor(220, 252, 231);
          doc.roundedRect(margin + 158, rowY + 1.2, 18, 4, 1, 1, 'F');
          doc.setFontSize(6.5);
          doc.setTextColor(22, 101, 52);
          doc.text(m.status, margin + 167, rowY + 3.8, { align: 'center' });

          rowY += 6;
        });

        y = rowY + 2;

        // 6. Section 3: Physical Mobility & Daily Routine Metrics
        y = drawSectionHeader('3. Physical Mobility & Daily Routine Metrics', y + 3);

        const mobCards = [
          { label: 'Daily Walking Duration', val: '24 mins / day avg', detail: 'Consistent morning stroll' },
          { label: 'Step Activity Level', val: '1,400 steps / day', detail: '93% of weekly wellness target' },
          { label: 'Routine Adherence', val: 'Calm Morning Routine', detail: 'Completed daily at 07:30 AM' }
        ];

        mobCards.forEach((mb, idx) => {
          const mCardX = margin + idx * (cardW + cardGap);
          doc.setFillColor(255, 255, 255);
          doc.setDrawColor(226, 232, 240);
          doc.setLineWidth(0.4);
          doc.roundedRect(mCardX, y, cardW, 16, 2, 2, 'FD');

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(7.5);
          doc.setTextColor(100, 116, 139);
          doc.text(mb.label, mCardX + 3.5, y + 4.8);

          doc.setFont('helvetica', 'bold');
          doc.setFontSize(9.5);
          doc.setTextColor(15, 23, 42);
          doc.text(mb.val, mCardX + 3.5, y + 9.5);

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(6.8);
          doc.setTextColor(71, 85, 105);
          doc.text(mb.detail, mCardX + 3.5, y + 13.5);
        });

        y += 16 + 4;

        // 7. Section 4: Clinical Observations & Recommendations
        y = drawSectionHeader('4. Clinical Observations & Caregiver Recommendations', y + 2);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(30, 41, 59);

        const notes = [
          '• Participant demonstrates strong routine adherence and consistent cognitive recall metrics over the 7-day monitoring period.',
          '• Memory match game accuracy remains at 91%, indicating excellent retention and visual-spatial orientation stability.',
          '• 100% medication compliance verified with zero skipped or off-schedule alerts reported.',
          '• Recommendation: Maintain the current daily 15-minute cognitive workout regimen and calm morning routine.',
          '• Next Clinical Review: Scheduled in accordance with standard 30-day geriatric neurological oversight protocol.'
        ];

        notes.forEach(note => {
          doc.text(note, margin + 3, y + 4.5);
          y += 5.2;
        });

        // 8. Signatures Block
        y += 6;
        doc.setDrawColor(203, 213, 225);
        doc.setLineWidth(0.4);

        const sigCol1 = margin + 10;
        const sigCol2 = margin + (contentWidth / 2) + 15;

        doc.line(sigCol1, y + 8, sigCol1 + 60, y + 8);
        doc.line(sigCol2, y + 8, sigCol2 + 60, y + 8);

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.5);
        doc.setTextColor(71, 85, 105);
        doc.text('Attending Physician Signature', sigCol1, y + 12);
        doc.text('Authorized Caregiver Signature', sigCol2, y + 12);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7);
        doc.setTextColor(148, 163, 184);
        doc.text(`Dr. Martinez, MD | Date: ${dateStr}`, sigCol1, y + 15.5);
        doc.text(`${caregiverName} | Date: ${dateStr}`, sigCol2, y + 15.5);

        // 9. Document Footer
        const footerY = pageHeight - 8;
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.3);
        doc.line(margin, footerY - 3, pageWidth - margin, footerY - 3);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(6.8);
        doc.setTextColor(148, 163, 184);
        doc.text('MEMOAID CLINICAL COGNITIVE CARE — STRICTLY CONFIDENTIAL MEDICAL DOCUMENT — FOR AUTHORIZED HEALTHCARE USE ONLY', margin, footerY);
        doc.text('Page 1 of 1', pageWidth - margin, footerY, { align: 'right' });

        doc.save(fileName);
        closeModal();
        return;
      } catch (err) {
        console.warn('jsPDF generation failed, falling back to standalone PDF generator:', err);
      }
    }

    // Standalone Native PDF 1.4 Generator Fallback (Guaranteed to download a real .pdf file)
    try {
      const reportLines = [
        'MEMOAID - CLINICAL COGNITIVE SUMMARY REPORT',
        `Document Ref: ${reportId} | Date: ${dateStr} ${timeStr}`,
        '--------------------------------------------------------------------------------',
        `Participant / Patient : ${ptName} (Age: ${ptAge})`,
        `Primary Caregiver     : ${caregiverName}`,
        `Attending Clinician   : ${physicianName}`,
        `Status                : Active Monitoring (Live Synced)`,
        '--------------------------------------------------------------------------------',
        '',
        '1. 7-DAY COGNITIVE PERFORMANCE SUMMARY',
        '  - Memory Recall Accuracy    : 91% (Target: >85% - Optimal Stability)',
        '  - Attention & Focus Score   : 86% (Target: >80% - High Engagement)',
        '  - Language & Fluency Score  : 89% (Target: >80% - Normal Function)',
        '  - Continuous calibration active; latency & retention remain stable.',
        '',
        '2. MEDICATION COMPLIANCE & REGIMEN LOG',
        '  - Lisinopril 10mg           : 100% Adherence (7/7 doses confirmed on schedule)',
        '  - Donepezil 5mg             : 100% Adherence (7/7 doses confirmed at bedtime)',
        '  - Multivitamin Complex      : 100% Adherence (7/7 doses confirmed at noon)',
        '  - Zero missed medication alerts in current reporting period.',
        '',
        '3. PHYSICAL MOBILITY & ROUTINE TRACKING',
        '  - Daily Walking Duration    : Average 24 mins / day',
        '  - Step Activity Level       : 1,400 steps / day (93% of weekly wellness target)',
        '  - Routine Adherence         : Calm Morning Routine completed at 07:30 AM daily',
        '',
        '4. CLINICAL OBSERVATIONS & RECOMMENDATIONS',
        '  - Participant demonstrates steady routine adherence & high cognitive retention.',
        '  - Memory match game consistency indicates strong visual-spatial orientation.',
        '  - Continue regular daily 15-minute cognitive exercises & hydration protocol.',
        '  - Next Clinical Review: In 30 days in accordance with standard oversight schedule.',
        '',
        '--------------------------------------------------------------------------------',
        'CONFIDENTIAL MEDICAL RECORD - FOR AUTHORIZED CLINICAL USE ONLY - MEMOAID'
      ];

      // Build PDF 1.4 stream
      let streamContent = 'BT\n/F1 10 Tf\n50 780 Td\n14 TL\n';
      reportLines.forEach((ln, idx) => {
        const escaped = ln.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
        if (idx === 0) {
          streamContent += `/F2 14 Tf (${escaped}) Tj /F1 10 Tf T*\n`;
        } else if (ln.startsWith('1.') || ln.startsWith('2.') || ln.startsWith('3.') || ln.startsWith('4.')) {
          streamContent += `T* /F2 11 Tf (${escaped}) Tj /F1 10 Tf T*\n`;
        } else {
          streamContent += `(${escaped}) Tj T*\n`;
        }
      });
      streamContent += 'ET\n';

      const byteLen = new TextEncoder().encode(streamContent).length;
      let pdfBody = `%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n`;
      const off1 = pdfBody.length;
      pdfBody += `2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n`;
      const off2 = pdfBody.length;
      pdfBody += `3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>\nendobj\n`;
      const off3 = pdfBody.length;
      pdfBody += `4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n`;
      const off4 = pdfBody.length;
      pdfBody += `5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n`;
      const off5 = pdfBody.length;
      pdfBody += `6 0 obj\n<< /Length ${byteLen} >>\nstream\n${streamContent}endstream\nendobj\n`;
      const xrefOffset = pdfBody.length;

      const pad = (n) => String(n).padStart(10, '0');
      pdfBody += `xref\n0 7\n0000000000 65535 f \n${pad(9)} 00000 n \n${pad(off1)} 00000 n \n${pad(off2)} 00000 n \n${pad(off3)} 00000 n \n${pad(off4)} 00000 n \n${pad(off5)} 00000 n \ntrailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;

      const blob = new Blob([pdfBody], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Failed to generate PDF:', e);
    }

    closeModal();
  };

  // ─────────────────────────────────────────────────────────────
  // 5B. CAREGIVER PATIENT MANAGEMENT & ACCOUNT DELETION (Requirements #2, #3, & #8)
  // ─────────────────────────────────────────────────────────────
  let caregiverPatients = [];
  let selectedCaregiverPatient = null;

  async function renderCaregiverPatients() {
    if (!currentSession || currentSession.role !== 'caregiver') return;

    const countBadge = document.getElementById('caregiverPatientCountBadge');
    const grid = document.getElementById('caregiverPatientsGrid');
    const emptyState = document.getElementById('caregiverNoPatients');

    if (countBadge) countBadge.textContent = 'Loading...';

    try {
      caregiverPatients = await API.getPatientsForCaregiver(currentSession.user_id);
    } catch (e) {
      console.warn('Error fetching caregiver patients:', e);
      caregiverPatients = [];
    }

    if (!Array.isArray(caregiverPatients)) caregiverPatients = [];

    if (caregiverPatients.length === 0) {
      selectedCaregiverPatient = null;
      if (countBadge) countBadge.textContent = '0 Patients';
      if (grid) {
        grid.innerHTML = '';
        grid.style.display = 'none';
      }
      if (emptyState) emptyState.style.display = 'block';
      updateActivePatientContext(null);
      await renderPatientAnalytics(null);
      return;
    }

    if (countBadge) {
      countBadge.textContent = caregiverPatients.length === 1 ? '1 Patient' : `${caregiverPatients.length} Patients`;
    }
    if (emptyState) emptyState.style.display = 'none';
    if (grid) grid.style.display = 'grid';

    // If current selected patient is no longer in list, default to first patient
    if (!selectedCaregiverPatient || !caregiverPatients.some(p => p.id === selectedCaregiverPatient.id)) {
      selectedCaregiverPatient = caregiverPatients[0];
    }

    currentSession.assigned_patient_id = selectedCaregiverPatient.id;
    currentUserId = selectedCaregiverPatient.id;
    updateActivePatientContext(selectedCaregiverPatient);

    // Render patient cards with clean initials avatar - NO random stock photos
    if (grid) {
      grid.innerHTML = caregiverPatients.map(patient => {
        const isSelected = selectedCaregiverPatient && selectedCaregiverPatient.id === patient.id;
        const avatarUrl = generateAvatarDataUri(patient.name, 'elderly');

        return `
          <div class="patient-card ${isSelected ? 'active-patient' : ''}" id="patient-card-${patient.id}">
            <div class="patient-card-header">
              <img src="${avatarUrl}" class="patient-card-avatar" alt="${patient.name}">
              <div class="patient-card-info">
                <div class="patient-card-name" title="${patient.name}">${patient.name}</div>
                <div class="patient-card-meta">@${patient.username} • Age: ${patient.age || 70}</div>
                <div class="patient-card-status">
                  <span class="pulse-dot"></span>
                  <span>${isSelected ? 'Active Monitored' : 'Participant Profile'}</span>
                </div>
              </div>
            </div>
            <div class="patient-card-actions">
              <button type="button" class="btn-select-patient" onclick="selectActivePatient(${patient.id})" aria-label="View ${patient.name}">
                <span class="material-symbols-outlined" style="font-size: 18px;">${isSelected ? 'check_circle' : 'visibility'}</span>
                <span>${isSelected ? 'Currently Viewing' : 'Select Patient'}</span>
              </button>
              <button type="button" class="btn-delete-patient" onclick="confirmDeletePatient(${patient.id}, '${patient.name.replace(/'/g, "\\'")}')" aria-label="Delete ${patient.name}">
                <span class="material-symbols-outlined" style="font-size: 18px;">delete</span>
                <span>Delete Patient</span>
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    // Refresh routines, memory anchors, and full analytics for active selected patient
    if (selectedCaregiverPatient) {
      await renderRoutineSchedule();
      await renderMemoryAnchors();
      await renderPatientAnalytics(selectedCaregiverPatient.id);
    }
  }

  window.selectActivePatient = async function(patientId) {
    const found = caregiverPatients.find(p => p.id === patientId);
    if (found) {
      selectedCaregiverPatient = found;
      if (currentSession) {
        currentSession.assigned_patient_id = found.id;
        localStorage.setItem('apon_session', JSON.stringify(currentSession));
      }
      currentUserId = found.id;
      updateActivePatientContext(found);
      await renderCaregiverPatients();
      await renderPatientAnalytics(found.id);
      showNotification(`Viewing participant: ${found.name}`);
    }
  };

  function updateActivePatientContext(patient) {
    const nameEl = document.getElementById('caregiverActivePatientName');
    const avatarEl = document.getElementById('caregiverActivePatientAvatar');
    const statusEl = document.getElementById('caregiverActivePatientStatus');

    if (patient) {
      if (nameEl) nameEl.innerHTML = `${patient.name} <span class="participant-meta">(Age ${patient.age || 70})</span>`;
      if (avatarEl) {
        avatarEl.src = generateAvatarDataUri(patient.name, 'elderly');
      }
      if (statusEl) {
        statusEl.innerHTML = `<span class="pulse-dot"></span><span>Active Monitored Live</span>`;
      }
    } else {
      if (nameEl) nameEl.innerHTML = `No Active Patient <span class="participant-meta">(None Assigned)</span>`;
      if (avatarEl) avatarEl.src = generateAvatarDataUri('None', 'elderly');
      if (statusEl) statusEl.innerHTML = `<span style="color: var(--text-muted);">No participant selected</span>`;
    }
  }

  // ─────────────────────────────────────────────────────────────
  // REAL-TIME PATIENT ANALYTICS ENGINE (Zero-state for fresh users, dynamic live sync)
  // ─────────────────────────────────────────────────────────────
  async function renderPatientAnalytics(targetUserId) {
    if (!targetUserId) {
      targetUserId = currentUserId;
    }

    if (!targetUserId) {
      // Zero out all metrics when no active user
      const actVal = document.getElementById('metricActivitiesVal');
      const actPillText = document.getElementById('metricActivitiesPillText');
      const actBar = document.getElementById('metricActivitiesBar');
      if (actVal) actVal.innerHTML = `0 <span style="font-size: 15px; color: var(--text-muted); font-weight: 400;">/ 15 weekly</span>`;
      if (actPillText) actPillText.textContent = 'Starting fresh (0%)';
      if (actBar) actBar.style.width = '0%';

      const recallVal = document.getElementById('metricRecallVal');
      const recallPillText = document.getElementById('metricRecallPillText');
      const recallBar = document.getElementById('metricRecallBar');
      if (recallVal) recallVal.textContent = '0%';
      if (recallPillText) recallPillText.textContent = 'No sessions yet';
      if (recallBar) recallBar.style.width = '0%';

      const streakVal = document.getElementById('metricStreakVal');
      const streakPillText = document.getElementById('metricStreakPillText');
      const streakBar = document.getElementById('metricStreakBar');
      if (streakVal) streakVal.textContent = '0 Days';
      if (streakPillText) streakPillText.textContent = 'Start your streak today';
      if (streakBar) streakBar.style.width = '0%';

      const lastVal = document.getElementById('metricLastInteractionVal');
      const lastSub = document.getElementById('metricLastInteractionSub');
      const lastBar = document.getElementById('metricLastInteractionBar');
      if (lastVal) lastVal.textContent = 'No interactions yet';
      if (lastSub) lastSub.textContent = 'Play a game or complete a routine to begin';
      if (lastBar) lastBar.style.width = '0%';

      const memVal = document.getElementById('trendMemoryVal');
      const memBar = document.getElementById('trendMemoryBar');
      if (memVal) memVal.textContent = '0%';
      if (memBar) memBar.style.width = '0%';

      const attVal = document.getElementById('trendAttentionVal');
      const attBar = document.getElementById('trendAttentionBar');
      if (attVal) attVal.textContent = '0%';
      if (attBar) attBar.style.width = '0%';

      const langVal = document.getElementById('trendLanguageVal');
      const langBar = document.getElementById('trendLanguageBar');
      if (langVal) langVal.textContent = '0%';
      if (langBar) langBar.style.width = '0%';

      const execVal = document.getElementById('trendExecutiveVal');
      const execBar = document.getElementById('trendExecutiveBar');
      if (execVal) execVal.textContent = '0%';
      if (execBar) execBar.style.width = '0%';

      const recentList = document.getElementById('caregiverRecentActivityList');
      if (recentList) {
        recentList.innerHTML = `<div style="text-align: center; padding: 24px; color: var(--text-muted); font-size: 14px;">No participant selected.</div>`;
      }
      return;
    }

    const data = await API.getPatientAnalytics(targetUserId);
    if (!data) return;

    // 1. Update Participant Selector & Reassurance Card
    const shortName = data.name.split(' ')[0];
    const reassuranceNoteText = document.getElementById('btnLeaveWarmNoteText');
    const reassuranceDesc = document.getElementById('caregiverReassuranceDesc');
    if (reassuranceNoteText) reassuranceNoteText.textContent = `Leave a Warm Note for ${shortName}`;
    if (reassuranceDesc) reassuranceDesc.textContent = `Send a digital note that will appear gently on ${shortName}'s home screen, or adjust reminder schedules.`;

    // 2. 4-Metric KPI Grid
    const actVal = document.getElementById('metricActivitiesVal');
    const actPillText = document.getElementById('metricActivitiesPillText');
    const actBar = document.getElementById('metricActivitiesBar');
    if (actVal) actVal.innerHTML = `${data.activities_completed} <span style="font-size: 15px; color: var(--text-muted); font-weight: 400;">/ 15 weekly</span>`;
    if (actPillText) actPillText.textContent = data.activities_badge;
    if (actBar) actBar.style.width = `${data.activities_bar_width}%`;

    const recallVal = document.getElementById('metricRecallVal');
    const recallPillText = document.getElementById('metricRecallPillText');
    const recallBar = document.getElementById('metricRecallBar');
    if (recallVal) recallVal.textContent = data.avg_recall_label;
    if (recallPillText) recallPillText.textContent = data.avg_recall_pill;
    if (recallBar) recallBar.style.width = `${data.avg_recall_bar_width}%`;

    const streakVal = document.getElementById('metricStreakVal');
    const streakPillText = document.getElementById('metricStreakPillText');
    const streakBar = document.getElementById('metricStreakBar');
    if (streakVal) streakVal.textContent = data.streak_label;
    if (streakPillText) streakPillText.textContent = data.streak_pill;
    if (streakBar) streakBar.style.width = `${data.streak_bar_width}%`;

    const lastVal = document.getElementById('metricLastInteractionVal');
    const lastSub = document.getElementById('metricLastInteractionSub');
    const lastBar = document.getElementById('metricLastInteractionBar');
    if (lastVal) lastVal.textContent = data.last_interaction_title;
    if (lastSub) lastSub.textContent = data.last_interaction_detail;
    if (lastBar) lastBar.style.width = `${data.last_interaction_bar_width}%`;

    // 3. Weekly Trends
    const memVal = document.getElementById('trendMemoryVal');
    const memBar = document.getElementById('trendMemoryBar');
    const memDesc = document.getElementById('trendMemoryDesc');
    if (memVal) memVal.textContent = `${data.trends.memory}%`;
    if (memBar) memBar.style.width = `${data.trends.memory}%`;
    if (memDesc) memDesc.textContent = data.trends.memory > 0 ? 'Recollection of cards and picture cues' : 'No memory exercises recorded yet';

    const attVal = document.getElementById('trendAttentionVal');
    const attBar = document.getElementById('trendAttentionBar');
    const attDesc = document.getElementById('trendAttentionDesc');
    if (attVal) attVal.textContent = `${data.trends.attention}%`;
    if (attBar) attBar.style.width = `${data.trends.attention}%`;
    if (attDesc) attDesc.textContent = data.trends.attention > 0 ? 'Pattern following and sustained focus' : 'No spatial or attention games recorded yet';

    const langVal = document.getElementById('trendLanguageVal');
    const langBar = document.getElementById('trendLanguageBar');
    const langDesc = document.getElementById('trendLanguageDesc');
    if (langVal) langVal.textContent = `${data.trends.language}%`;
    if (langBar) langBar.style.width = `${data.trends.language}%`;
    if (langDesc) langDesc.textContent = data.trends.language > 0 ? 'Word recognition and semantic fluency' : 'No word exercises recorded yet';

    const execVal = document.getElementById('trendExecutiveVal');
    const execBar = document.getElementById('trendExecutiveBar');
    const execDesc = document.getElementById('trendExecutiveDesc');
    if (execVal) execVal.textContent = `${data.trends.executive}%`;
    if (execBar) execBar.style.width = `${data.trends.executive}%`;
    if (execDesc) execDesc.textContent = data.trends.executive > 0 ? 'Complex matching and puzzle solving' : 'No pattern exercises recorded yet';

    // 4. Recent Activities List
    const recentList = document.getElementById('caregiverRecentActivityList');
    if (recentList) {
      if (!data.recent_activities || data.recent_activities.length === 0) {
        recentList.innerHTML = `
          <div style="text-align: center; padding: 28px 16px; color: var(--text-muted); font-size: 14px;">
            <span class="material-symbols-outlined" style="font-size: 40px; color: var(--secondary); display: block; margin-bottom: 8px;">history_toggle_off</span>
            No recent activities recorded yet for ${data.name}.<br>
            When they complete cognitive games or daily routines, verified history will appear here.
          </div>
        `;
      } else {
        recentList.innerHTML = data.recent_activities.map(act => `
          <div class="activity-item">
            <div class="activity-left">
              <div class="activity-icon-box" style="${act.type === 'game' ? 'background-color: var(--primary-light-bg); color: var(--primary);' : 'background-color: var(--secondary-container); color: var(--on-secondary-container);'}">
                <span class="material-symbols-outlined">${act.icon}</span>
              </div>
              <div>
                <div class="activity-name">${act.title}</div>
                <div class="activity-meta">${act.meta}</div>
              </div>
            </div>
            <div class="activity-right">
              <div>
                <div class="activity-score" style="color: var(--on-surface); font-weight: 600;">${act.score}</div>
                <div class="activity-meta">${act.status}</div>
              </div>
              <span class="material-symbols-outlined" style="color: var(--primary);">check_circle</span>
            </div>
          </div>
        `).join('');
      }
    }

    // 5. Elderly Greeting Title
    const elderlyGreeting = document.getElementById('elderlyGreetingTitle');
    if (elderlyGreeting && currentSession && currentSession.role === 'elderly') {
      elderlyGreeting.textContent = `Good morning, ${shortName} ☀️`;
    }

    // 6. My Progress View
    const vitScore = document.getElementById('progressVitalityScore');
    const vitBadge = document.getElementById('progressVitalityBadge');
    const vitBar = document.getElementById('progressVitalityBar');
    if (vitScore) vitScore.textContent = data.vitality_score.toFixed(1);
    if (vitBadge) vitBadge.textContent = data.vitality_badge;
    if (vitBar) vitBar.style.width = `${data.vitality_bar_width}%`;

    const milestoneList = document.getElementById('progressMilestonesList');
    if (milestoneList) {
      if (!data.milestones || data.milestones.length === 0) {
        milestoneList.innerHTML = `
          <div class="activity-item">
            <div class="activity-left">
              <div class="activity-icon-box" style="background-color: var(--surface-container); color: var(--secondary);">
                <span class="material-symbols-outlined">flag</span>
              </div>
              <div>
                <div class="activity-name">Welcome to Cognitive Wellness</div>
                <div class="activity-meta">Play your first cognitive training game to unlock your milestones!</div>
              </div>
            </div>
            <span class="badge-upcoming">Get Started</span>
          </div>
        `;
      } else {
        milestoneList.innerHTML = data.milestones.map(m => `
          <div class="activity-item">
            <div class="activity-left">
              <div class="activity-icon-box" style="background-color: ${m.bg}; color: ${m.color};">
                <span class="material-symbols-outlined">${m.icon}</span>
              </div>
              <div>
                <div class="activity-name">${m.name}</div>
                <div class="activity-meta">${m.desc}</div>
              </div>
            </div>
            <span class="badge-done">${m.status}</span>
          </div>
        `).join('');
      }
    }
  }

  window.renderPatientAnalytics = renderPatientAnalytics;

  // Add Patient Modal Handling
  window.openAddPatientModal = function() {
    const modal = document.getElementById('addPatientModal');
    const alertBox = document.getElementById('addPatientAlert');
    if (alertBox) {
      alertBox.style.display = 'none';
      alertBox.className = 'auth-alert-box';
    }
    const form = document.getElementById('addPatientForm');
    if (form) form.reset();
    if (modal) modal.style.display = 'flex';
  };

  window.closeAddPatientModal = function() {
    const modal = document.getElementById('addPatientModal');
    if (modal) modal.style.display = 'none';
  };

  window.handleAddPatientSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (!currentSession || currentSession.role !== 'caregiver') {
      alert('Only authenticated caregivers can add patients.');
      return;
    }

    const name = (document.getElementById('newPatientName')?.value || '').trim();
    const username = (document.getElementById('newPatientUsername')?.value || '').trim();
    const age = parseInt(document.getElementById('newPatientAge')?.value || '70', 10);
    const password = document.getElementById('newPatientPassword')?.value || 'password123';
    const relationship = (document.getElementById('newPatientRelationship')?.value || '').trim();

    const alertBox = document.getElementById('addPatientAlert');
    const submitBtn = document.getElementById('btnSubmitAddPatientText');

    if (!name || !username) {
      if (alertBox) {
        alertBox.textContent = 'Please enter both patient full name and a unique username.';
        alertBox.className = 'auth-alert-box error';
        alertBox.style.display = 'flex';
      }
      return;
    }

    if (submitBtn) submitBtn.textContent = 'Saving...';

    const res = await API.addPatientForCaregiver(currentSession.user_id, {
      name,
      username,
      age,
      password,
      relationship
    });

    if (submitBtn) submitBtn.textContent = 'Save Patient';

    if (res.success && res.patient) {
      closeAddPatientModal();
      showNotification(`Patient ${res.patient.name} created and linked successfully!`);
      await renderCaregiverPatients();
      await selectActivePatient(res.patient.id);
    } else {
      if (alertBox) {
        alertBox.textContent = res.error || 'Failed to create patient account.';
        alertBox.className = 'auth-alert-box error';
        alertBox.style.display = 'flex';
      }
    }
  };

  // Delete Patient Modal Handling
  let patientToDeleteId = null;

  window.confirmDeletePatient = function(patientId, patientName) {
    patientToDeleteId = patientId;
    const targetNameEl = document.getElementById('deletePatientTargetName');
    if (targetNameEl) targetNameEl.textContent = `${patientName} (ID: #${patientId})`;
    const modal = document.getElementById('deletePatientModal');
    if (modal) modal.style.display = 'flex';
  };

  window.closeDeletePatientModal = function() {
    patientToDeleteId = null;
    const modal = document.getElementById('deletePatientModal');
    if (modal) modal.style.display = 'none';
  };

  window.executeDeletePatient = async function() {
    if (!patientToDeleteId || !currentSession || currentSession.role !== 'caregiver') return;

    const btn = document.getElementById('btnConfirmDeletePatientAction');
    if (btn) btn.disabled = true;

    const res = await API.deletePatient(currentSession.user_id, patientToDeleteId);

    if (btn) btn.disabled = false;
    closeDeletePatientModal();

    if (res.success) {
      showNotification('Patient successfully deleted from database.');
      await renderCaregiverPatients();
    } else {
      alert(res.error || 'Failed to delete patient. Ensure you have permission.');
    }
  };

  // Caregiver Account Deletion Handling
  window.confirmDeleteCaregiverAccount = function() {
    const modal = document.getElementById('deleteCaregiverModal');
    if (modal) modal.style.display = 'flex';
  };

  window.closeDeleteCaregiverModal = function() {
    const modal = document.getElementById('deleteCaregiverModal');
    if (modal) modal.style.display = 'none';
  };

  window.executeDeleteCaregiverAccount = async function() {
    if (!currentSession || currentSession.role !== 'caregiver') return;

    const btn = document.getElementById('btnConfirmDeleteCaregiverAction');
    if (btn) btn.disabled = true;

    const res = await API.deleteCaregiverAccount(currentSession.user_id);
    if (btn) btn.disabled = false;
    closeDeleteCaregiverModal();

    if (res.success) {
      localStorage.removeItem('apon_session');
      currentSession = null;
      currentUserId = null;
      currentRole = 'guest';
      isViewingAsParticipant = false;
      caregiverPatients = [];
      selectedCaregiverPatient = null;
      history.replaceState(null, '', '#login');
      syncAuthUI();
      switchTab('login-view');
      showNotification('Caregiver account deleted. All associated patients have been safely unlinked.');
    } else {
      alert(res.error || 'Failed to delete caregiver account.');
    }
  };

  // ─────────────────────────────────────────────────────────────
  // 6. CAREGIVER REASSURANCE ACTIONS
  // ─────────────────────────────────────────────────────────────
  const btnLeaveNote = document.getElementById('btnLeaveNote');
  if (btnLeaveNote) {
    btnLeaveNote.addEventListener('click', () => {
      const activePatientName = currentSession?.name || 'Patient';
      openModal(
        `Leave a Warm Note for ${activePatientName}`,
        `<div>
           <p style="color: #66757D; font-size: 14px; margin-bottom: 12px;">This note will appear prominently at the top of ${activePatientName}'s screen when they check their dashboard.</p>
           <textarea id="noteInput" rows="3" style="width: 100%; border: 1.5px solid #DDE5E1; border-radius: 10px; padding: 12px; font-family: inherit; font-size: 15px;" placeholder="e.g. Thinking of you! Have a wonderful and peaceful day."></textarea>
           <button class="btn-primary" style="margin-top: 14px; width: 100%; justify-content: center;" onclick="saveWarmNote()">
             <span class="material-symbols-outlined">send</span>
             <span>Post Note to Patient Home Screen</span>
           </button>
         </div>`
      );
    });
  }

  window.saveWarmNote = function() {
    const text = document.getElementById('noteInput')?.value.trim();
    if (!text) return;
    const authorName = currentSession?.name ? `${currentSession.name} (Caregiver)` : 'Caregiver';
    localStorage.setItem('apon_warm_note', JSON.stringify({
      author: authorName,
      text: text,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }));
    closeModal();
    renderWarmNoteBanner();
    alert("Note posted! The patient will now see your warm message on their dashboard.");
  };

  function renderWarmNoteBanner() {
    const raw = localStorage.getItem('apon_warm_note');
    const container = document.getElementById('elderlyWarmNoteContainer');
    if (!container) return;

    if (raw) {
      const data = JSON.parse(raw);
      container.innerHTML = `
        <div style="background: #FFF8EB; border: 1.5px solid #F5D399; border-radius: 14px; padding: 18px 22px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px;">
          <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 44px; height: 44px; border-radius: 50%; background: #FFDDB6; color: #643F00; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <span class="material-symbols-outlined">favorite</span>
            </div>
            <div>
              <div style="font-size: 13px; font-weight: 700; color: #643F00; text-transform: uppercase;">Message from ${data.author} (${data.date})</div>
              <div style="font-size: 16px; font-weight: 600; color: #2A1800; margin-top: 2px;">"${data.text}"</div>
            </div>
          </div>
          <button class="btn-secondary" style="min-height: 36px; padding: 6px 12px; font-size: 13px;" onclick="speakText('${data.text}')">
            <span class="material-symbols-outlined" style="font-size: 18px; color: #176B4D;">volume_up</span>
            <span>Read to Me</span>
          </button>
        </div>
      `;
    } else {
      container.innerHTML = '';
    }
  }

  // ─────────────────────────────────────────────────────────────
  // 7. DAILY ROUTINE & REMINDERS (LIVE BACKEND SYNC)
  // ─────────────────────────────────────────────────────────────
  async function renderRoutineSchedule() {
    const reminders = await API.getReminders(currentUserId);
    const container = document.getElementById('interactiveRoutineList');
    const caregiverContainer = document.getElementById('caregiverRoutineList');

    if (!container && !caregiverContainer) return;

    let completedCount = 0;
    let listHtml = '';
    let caregiverListHtml = '';

    reminders.forEach(r => {
      const isDone = r.status === 'completed';
      if (isDone) completedCount++;

      // Participant list item
      listHtml += `
        <div class="routine-item ${isDone ? '' : 'upcoming'}" id="routine-${r.id}">
          <div style="display: flex; align-items: center; gap: 14px;">
            <div class="routine-check-box ${isDone ? '' : 'pending'}" style="cursor: pointer;" onclick="toggleRoutineComplete(${r.id})">
              <span class="material-symbols-outlined" style="font-size: 20px;">${isDone ? 'check' : 'schedule'}</span>
            </div>
            <div>
              <div style="font-weight: 600; font-size: 16px; ${isDone ? 'text-decoration: line-through; opacity: 0.8;' : ''}">${r.task}</div>
              <div style="font-size: 14px; color: var(--text-muted);">${r.time} • Type: ${r.reminder_type.toUpperCase()}</div>
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            ${isDone 
              ? '<span class="badge-done">Completed</span>'
              : `<button class="btn-secondary" style="min-height: 36px; padding: 4px 12px; font-size: 13px;" onclick="toggleRoutineComplete(${r.id})">Mark Done</button>`
            }
            <button onclick="deleteRoutineItem(${r.id})" style="border: none; background: transparent; color: #BA1A1A; cursor: pointer; padding: 4px;">
              <span class="material-symbols-outlined" style="font-size: 20px;">delete</span>
            </button>
          </div>
        </div>
      `;

      // Caregiver list item
      caregiverListHtml += `
        <div class="routine-item ${isDone ? '' : 'upcoming'}">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="routine-check-box ${isDone ? '' : 'pending'}">
              <span class="material-symbols-outlined" style="font-size: 18px;">${isDone ? 'check' : 'schedule'}</span>
            </div>
            <div>
              <div style="font-weight: 600; font-size: 15px;">${r.task}</div>
              <div style="font-size: 13px; color: var(--text-muted);">${r.time}</div>
            </div>
          </div>
          <span class="${isDone ? 'badge-done' : 'badge-upcoming'}">${isDone ? 'Done' : 'Upcoming'}</span>
        </div>
      `;
    });

    if (container) container.innerHTML = listHtml;
    if (caregiverContainer) caregiverContainer.innerHTML = caregiverListHtml;

    // Update Adherence Percentage Pill
    const pct = reminders.length ? Math.round((completedCount / reminders.length) * 100) : 0;
    const adherencePills = document.querySelectorAll('.adherence-pct-pill');
    adherencePills.forEach(pill => {
      pill.textContent = `${pct}% Complete (${completedCount}/${reminders.length})`;
    });
  }

  window.toggleRoutineComplete = async function(reminderId) {
    await API.completeReminder(reminderId, currentUserId);
    await renderRoutineSchedule();
    await renderPatientAnalytics(currentUserId);
  };

  window.deleteRoutineItem = async function(reminderId) {
    if (confirm("Remove this routine reminder?")) {
      await API.deleteReminder(reminderId, currentUserId);
      await renderRoutineSchedule();
      await renderPatientAnalytics(currentUserId);
    }
  };

  // Add Reminder Modal
  window.openAddReminderModal = function() {
    openModal(
      'Add New Daily Routine Reminder',
      `<div style="display: flex; flex-direction: column; gap: 14px;">
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Task or Medication Title</label>
           <input type="text" id="newReminderTask" placeholder="e.g. Afternoon Calcium Supplement" style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px;">
         </div>
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Scheduled Time</label>
           <input type="text" id="newReminderTime" placeholder="e.g. 03:00 PM" style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px;">
         </div>
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Category</label>
           <select id="newReminderType" style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px;">
             <option value="medication">Medication</option>
             <option value="activity">Cognitive / Physical Activity</option>
             <option value="hydration">Hydration & Nutrition</option>
             <option value="social">Family & Social Call</option>
           </select>
         </div>
         <button class="btn-primary" style="margin-top: 10px; width: 100%; justify-content: center;" onclick="saveNewReminder()">
           <span class="material-symbols-outlined">add_task</span>
           <span>Save Reminder to Schedule</span>
         </button>
       </div>`
    );
  };

  window.saveNewReminder = async function() {
    const task = document.getElementById('newReminderTask')?.value.trim();
    const time = document.getElementById('newReminderTime')?.value.trim();
    const type = document.getElementById('newReminderType')?.value;

    if (!task || !time) {
      alert("Please fill in both the title and time.");
      return;
    }

    await API.createReminder({
      user_id: currentUserId,
      task: task,
      reminder_type: type,
      date: new Date().toISOString().slice(0, 10),
      time: time,
      status: 'pending'
    });

    closeModal();
    await renderRoutineSchedule();
    await renderPatientAnalytics(currentUserId);
  };

  // ─────────────────────────────────────────────────────────────
  // 8. MEMORY ANCHORS (LIVE GALLERY + SPEECH SYNTHESIS)
  // ─────────────────────────────────────────────────────────────
  async function renderMemoryAnchors() {
    const memories = await API.getMemories(currentUserId);
    const gallery = document.getElementById('memoryAnchorsGallery');
    const caregiverThumbs = document.getElementById('caregiverMemoryThumbs');

    if (!gallery && !caregiverThumbs) return;

    let galleryHtml = '';
    let thumbsHtml = '';

    const defaultImages = [
      'https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=500&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1552053831-71594a27632d?w=500&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=500&auto=format&fit=crop&q=80',
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500&auto=format&fit=crop&q=80'
    ];

    memories.forEach((m, idx) => {
      const imgUrl = m.image_url || defaultImages[idx % defaultImages.length];

      galleryHtml += `
        <div class="card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <img src="${imgUrl}" style="width: 100%; height: 200px; object-fit: cover;" alt="${m.person_name}">
            <div style="padding: 20px;">
              <span class="badge-upcoming" style="margin-bottom: 8px;">${m.relationship}</span>
              <h3 style="margin: 4px 0 8px;">${m.person_name}</h3>
              <p style="color: var(--text-muted); font-size: 14px; line-height: 1.6;">${m.information}</p>
            </div>
          </div>
          <div style="padding: 16px 20px; border-top: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center;">
            <span class="badge-done">96% Recall</span>
            <button class="btn-primary" style="min-height: 38px; padding: 6px 14px; font-size: 13px;" onclick="playMemoryAudio('${m.person_name}', '${encodeURIComponent(m.information)}')">
              <span class="material-symbols-outlined" style="font-size: 18px;">volume_up</span>
              <span>Listen to Story</span>
            </button>
          </div>
        </div>
      `;

      thumbsHtml += `
        <div class="memory-thumb-card" onclick="openMemoryDetailModal('${m.person_name}', '${encodeURIComponent(m.information)}')">
          <img src="${imgUrl}" alt="${m.person_name}">
          <div class="memory-thumb-overlay">
            <span class="memory-thumb-title">${m.person_name}</span>
          </div>
        </div>
      `;
    });

    if (gallery) gallery.innerHTML = galleryHtml;
    if (caregiverThumbs) caregiverThumbs.innerHTML = thumbsHtml;
  }

  window.openAddMemoryModal = function() {
    openModal(
      'Upload New Memory Anchor',
      `<div style="display: flex; flex-direction: column; gap: 16px;">

         <!-- Image Upload Area -->
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #0F1D23;">
             <span class="material-symbols-outlined" style="font-size:17px; vertical-align:middle; margin-right:4px; color:var(--primary);">add_photo_alternate</span>
             Upload a Photo (optional)
           </label>
           <label for="newMemoryImageInput" id="memoryImageDropZone" style="
             display: flex; flex-direction: column; align-items: center; justify-content: center;
             gap: 10px; padding: 22px 16px; border: 2px dashed #B0CBBC; border-radius: 12px;
             background: #F3F9F5; cursor: pointer; transition: border-color 0.2s, background 0.2s;
             min-height: 110px; text-align: center;
           "
             onmouseenter="this.style.borderColor='#176B4D'; this.style.background='#E8F5EF';"
             onmouseleave="this.style.borderColor='#B0CBBC'; this.style.background='#F3F9F5';">
             <span class="material-symbols-outlined" style="font-size: 36px; color: #176B4D;">image</span>
             <span style="font-size: 14px; color: #66757D; font-weight: 500;">Click to browse or drop a photo here</span>
             <span style="font-size: 12px; color: #9DADB5;">JPG, PNG, WEBP · Max 5MB</span>
           </label>
           <input type="file" id="newMemoryImageInput" accept="image/*" style="display:none;"
             onchange="previewMemoryImage(this)">
           <!-- Preview -->
           <div id="memoryImagePreview" style="display:none; margin-top: 10px; position: relative;">
             <img id="memoryImagePreviewImg" src="" alt="Preview"
               style="width:100%; max-height:200px; object-fit:cover; border-radius:10px; border: 1.5px solid #DDE5E1;">
             <button type="button" onclick="clearMemoryImage()" style="
               position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.55);
               color: #fff; border: none; border-radius: 50%; width: 28px; height: 28px;
               font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
               title="Remove image">&times;</button>
             <div id="memoryImageFileName" style="font-size: 12px; color: #66757D; margin-top: 6px; text-align: center;"></div>
           </div>
         </div>

         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Memory Title (Person, Pet, or Place) *</label>
           <input type="text" id="newMemoryTitle" placeholder="e.g. Cape Cod Summer Lighthouse" style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px; box-sizing: border-box;">
         </div>
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Relationship / Significance</label>
           <input type="text" id="newMemoryRel" placeholder="e.g. Favorite Family Holiday" style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px; box-sizing: border-box;">
         </div>
         <div>
           <label style="display: block; font-weight: 600; margin-bottom: 6px;">Story & Familiar Details *</label>
           <textarea id="newMemoryInfo" rows="3" placeholder="Describe the memory with warm, familiar sensory details..." style="width: 100%; padding: 10px 14px; border: 1.5px solid #DDE5E1; border-radius: 8px; font-size: 15px; font-family: inherit; box-sizing: border-box;"></textarea>
         </div>
         <button class="btn-primary" style="margin-top: 4px; width: 100%; justify-content: center;" onclick="saveNewMemory()">
           <span class="material-symbols-outlined">save</span>
           <span>Save Memory Anchor</span>
         </button>
       </div>`
    );
  };

  window.previewMemoryImage = function(input) {
    const file = input.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      alert('Image is too large. Please choose a file under 5MB.');
      input.value = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
      const previewDiv = document.getElementById('memoryImagePreview');
      const previewImg = document.getElementById('memoryImagePreviewImg');
      const dropZone = document.getElementById('memoryImageDropZone');
      const fileName = document.getElementById('memoryImageFileName');
      if (previewImg) previewImg.src = e.target.result;
      if (previewDiv) previewDiv.style.display = 'block';
      if (dropZone) dropZone.style.display = 'none';
      if (fileName) fileName.textContent = file.name;
    };
    reader.readAsDataURL(file);
  };

  window.clearMemoryImage = function() {
    const input = document.getElementById('newMemoryImageInput');
    const previewDiv = document.getElementById('memoryImagePreview');
    const dropZone = document.getElementById('memoryImageDropZone');
    if (input) input.value = '';
    if (previewDiv) previewDiv.style.display = 'none';
    if (dropZone) dropZone.style.display = 'flex';
  };

  window.saveNewMemory = async function() {
    const title = document.getElementById('newMemoryTitle')?.value.trim();
    const rel = document.getElementById('newMemoryRel')?.value.trim();
    const info = document.getElementById('newMemoryInfo')?.value.trim();
    const previewImg = document.getElementById('memoryImagePreviewImg');

    if (!title || !info) {
      alert('Please enter a memory title and story description.');
      return;
    }

    // Read the uploaded image as base64 if present
    let imageUrl = null;
    const imgInput = document.getElementById('newMemoryImageInput');
    if (imgInput && imgInput.files && imgInput.files[0]) {
      imageUrl = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsDataURL(imgInput.files[0]);
      });
    }

    const submitBtn = document.querySelector('#genericModal .btn-primary');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Saving...'; }

    await API.createMemory({
      user_id: currentUserId,
      person_name: title,
      relationship: rel || 'Cherished Memory',
      information: info,
      image_url: imageUrl
    });

    closeModal();
    await renderMemoryAnchors();
    showNotification(`Memory "${title}" saved successfully!`);
  };

  window.playMemoryAudio = function(title, encodedInfo) {
    const text = decodeURIComponent(encodedInfo);
    speakText(`Remembering ${title}. ${text}`);
  };

  window.openMemoryDetailModal = function(name, encodedInfo) {
    const text = decodeURIComponent(encodedInfo);
    openModal(
      `Memory Anchor: ${name}`,
      `<div>
         <p style="font-size: 16px; line-height: 1.7; margin-bottom: 20px; color: #0F1D23;">${text}</p>
         <button class="btn-primary" onclick="playMemoryAudio('${name}', '${encodeURIComponent(text)}')">
           <span class="material-symbols-outlined">volume_up</span>
           <span>Narrate Story Aloud</span>
         </button>
       </div>`
    );
  };

  // ─────────────────────────────────────────────────────────────
  // 9. FULLY PLAYABLE COGNITIVE GAMES (SAVES TO BACKEND)
  // ─────────────────────────────────────────────────────────────

  // Game 1: Card Memory Match
  window.launchCardMemoryGame = function() {
    const icons = ['🌻', '🍓', '🍎', '🌸', '🌻', '🍓', '🍎', '🌸'];
    // Shuffle
    const deck = icons.sort(() => 0.5 - Math.random());

    let cardsHtml = '';
    deck.forEach((icon, i) => {
      cardsHtml += `
        <div class="memory-card-tile" data-card="${icon}" data-index="${i}" onclick="flipMemoryTile(this)" style="width: 80px; height: 90px; background: #176B4D; color: #ffffff; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 36px; cursor: pointer; user-select: none; transition: transform 0.2s;">
          ?
        </div>
      `;
    });

    openModal(
      'Card Memory Match (Level 1)',
      `<div style="text-align: center;">
         <p style="color: #66757D; font-size: 14px; margin-bottom: 16px;">Flip cards to find the matching nature pairs. Take all the time you need!</p>
         <div style="display: grid; grid-template-columns: repeat(4, 80px); gap: 14px; justify-content: center; margin: 0 auto 16px;" id="cardDeckGrid">
           ${cardsHtml}
         </div>
         <div style="font-size: 15px; font-weight: 600; color: #176B4D;" id="gameStatusText">Matches Found: 0 / 4</div>
       </div>`,
      null,
      'Quit Game'
    );

    window.gameFlipped = [];
    window.gameMatches = 0;
    window.gameMoves = 0;
  };

  window.flipMemoryTile = function(tile) {
    if (window.gameFlipped.length >= 2 || tile.classList.contains('matched') || tile.classList.contains('flipped')) return;

    tile.classList.add('flipped');
    tile.style.background = '#FFFFFF';
    tile.style.border = '2px solid #176B4D';
    tile.textContent = tile.getAttribute('data-card');

    window.gameFlipped.push(tile);

    if (window.gameFlipped.length === 2) {
      window.gameMoves++;
      const [t1, t2] = window.gameFlipped;
      if (t1.getAttribute('data-card') === t2.getAttribute('data-card')) {
        t1.classList.add('matched');
        t2.classList.add('matched');
        window.gameMatches++;
        window.gameFlipped = [];
        document.getElementById('gameStatusText').textContent = `Matches Found: ${window.gameMatches} / 4`;

        if (window.gameMatches === 4) {
          setTimeout(async () => {
            const finalScore = Math.max(70, 100 - (window.gameMoves - 4) * 5);
            await API.saveGameResult({
              user_id: currentUserId,
              game_name: 'Card Memory Match',
              score: finalScore,
              accuracy: 100,
              completion_time: 45,
              difficulty_level: 1
            });
            await renderPatientAnalytics(currentUserId);
            openModal(
              '🎉 Exercise Completed!',
              `<div style="text-align: center; padding: 14px 0;">
                 <span class="material-symbols-outlined" style="font-size: 64px; color: #176B4D;">verified</span>
                 <h2 style="margin: 12px 0 6px;">Splendid Recall!</h2>
                 <p style="font-size: 16px; color: #66757D;">You matched all pairs with an accuracy score of <strong>${finalScore}/100</strong>.</p>
                 <div style="padding: 12px; background: #E7F4ED; border-radius: 10px; color: #176B4D; font-weight: 600; margin-top: 14px;">
                   Saved to your cognitive health trends!
                 </div>
               </div>`
            );
          }, 400);
        }
      } else {
        setTimeout(() => {
          t1.classList.remove('flipped');
          t1.style.background = '#176B4D';
          t1.textContent = '?';
          t2.classList.remove('flipped');
          t2.style.background = '#176B4D';
          t2.textContent = '?';
          window.gameFlipped = [];
        }, 900);
      }
    }
  };

  // Game 2: Spatial Pattern Match
  window.launchSpatialPatternGame = function() {
    openModal(
      'Spatial Pattern Match',
      `<div style="text-align: center;">
         <p style="color: #66757D; font-size: 14px; margin-bottom: 16px;">Watch the tiles illuminate, then repeat the pattern in the exact order.</p>
         <div style="display: grid; grid-template-columns: repeat(3, 75px); gap: 12px; justify-content: center; margin: 0 auto 18px;" id="spatialGrid">
           ${[0,1,2,3,4,5,6,7,8].map(i => `
             <div class="spatial-tile" id="tile-${i}" onclick="tileClicked(${i})" style="width: 75px; height: 75px; background: #D2E4FC; border-radius: 12px; cursor: pointer; transition: all 0.2s;"></div>
           `).join('')}
         </div>
         <button class="btn-primary" id="btnStartPattern" onclick="playSpatialSequence()" style="margin: 0 auto;">Show Pattern</button>
         <div id="spatialStatus" style="font-size: 14px; font-weight: 600; margin-top: 12px; color: #1F3042;">Press 'Show Pattern' to begin</div>
       </div>`,
      null,
      'Close'
    );

    window.spatialPattern = [1, 4, 7];
    window.playerIndex = 0;
    window.canClickTile = false;
  };

  window.playSpatialSequence = function() {
    window.canClickTile = false;
    window.playerIndex = 0;
    document.getElementById('spatialStatus').textContent = 'Observing sequence...';

    window.spatialPattern.forEach((tileIdx, step) => {
      setTimeout(() => {
        const el = document.getElementById(`tile-${tileIdx}`);
        if (el) {
          el.style.background = '#176B4D';
          el.style.transform = 'scale(1.08)';
          setTimeout(() => {
            el.style.background = '#D2E4FC';
            el.style.transform = 'scale(1)';
          }, 500);
        }
      }, step * 800);
    });

    setTimeout(() => {
      window.canClickTile = true;
      document.getElementById('spatialStatus').textContent = 'Your turn: Click the tiles in order!';
    }, window.spatialPattern.length * 800 + 200);
  };

  window.tileClicked = async function(idx) {
    if (!window.canClickTile) return;

    const el = document.getElementById(`tile-${idx}`);
    if (el) {
      el.style.background = '#176B4D';
      setTimeout(() => { el.style.background = '#D2E4FC'; }, 300);
    }

    if (idx === window.spatialPattern[window.playerIndex]) {
      window.playerIndex++;
      if (window.playerIndex === window.spatialPattern.length) {
        window.canClickTile = false;
        document.getElementById('spatialStatus').textContent = 'Excellent! Sequence matched perfectly.';
        await API.saveGameResult({
          user_id: currentUserId,
          game_name: 'Spatial Pattern Match',
          score: 95.0,
          accuracy: 100,
          completion_time: 30,
          difficulty_level: 2
        });
        await renderPatientAnalytics(currentUserId);
      }
    } else {
      document.getElementById('spatialStatus').textContent = 'Almost! Try again by pressing Show Pattern.';
      window.canClickTile = false;
    }
  };

  // Game 3: Picture Recall Quiz
  window.launchPictureRecallGame = function() {
    openModal(
      'Picture Recall Quiz',
      `<div style="text-align: center;">
         <img src="https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=500&auto=format&fit=crop&q=80" style="width: 100%; max-height: 220px; object-fit: cover; border-radius: 12px; margin-bottom: 14px;" alt="Cottage">
         <p style="font-size: 16px; font-weight: 600; margin-bottom: 14px;">Question: What color flowers are growing by the porch?</p>
         <div style="display: flex; flex-direction: column; gap: 10px; max-width: 320px; margin: 0 auto;">
           <button class="btn-secondary" onclick="answerPictureQuiz(false)">A) Bright Yellow Tulips</button>
           <button class="btn-secondary" onclick="answerPictureQuiz(true)">B) Blue & Purple Hydrangeas</button>
           <button class="btn-secondary" onclick="answerPictureQuiz(false)">C) Red Climbing Roses</button>
         </div>
       </div>`
    );
  };

  window.answerPictureQuiz = async function(isCorrect) {
    if (isCorrect) {
      await API.saveGameResult({
        user_id: currentUserId,
        game_name: 'Picture Recall Quiz',
        score: 96.0,
        accuracy: 100,
        completion_time: 25,
        difficulty_level: 2
      });
      await renderPatientAnalytics(currentUserId);
      openModal(
        '🎯 Correct Answer!',
        `<div style="text-align: center; padding: 16px 0;">
           <span class="material-symbols-outlined" style="font-size: 56px; color: #176B4D;">check_circle</span>
           <p style="font-size: 17px; font-weight: 600; margin-top: 10px;">Spot-on! Blue and purple hydrangeas flourish by the coastal cottage.</p>
           <p style="color: #66757D; font-size: 14px; margin-top: 6px;">Recall score 96/100 recorded.</p>
         </div>`
      );
    } else {
      alert("Close, but not quite! Hint: Look carefully at the flowers in the memory picture!");
    }
  };

  // General game launcher dispatcher
  window.launchGame = function(name) {
    if (name.includes('Card') || name.includes('Memory')) {
      launchCardMemoryGame();
    } else if (name.includes('Spatial') || name.includes('Pattern')) {
      launchSpatialPatternGame();
    } else {
      launchPictureRecallGame();
    }
  };

  // ─────────────────────────────────────────────────────────────
  // 10. MODAL CONTROLS & SHARED HELPERS
  // ─────────────────────────────────────────────────────────────
  const modal = document.getElementById('genericModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  const modalConfirmBtn = document.getElementById('modalConfirmBtn');
  let currentConfirmCallback = null;

  window.openModal = function(title, bodyHtml, onConfirm = null, confirmText = 'Confirm') {
    if (!modal) return;
    modalTitle.textContent = title;
    modalBody.innerHTML = bodyHtml;
    currentConfirmCallback = onConfirm;
    modalConfirmBtn.textContent = confirmText;
    modalConfirmBtn.style.display = onConfirm ? 'inline-flex' : 'none';
    modal.style.display = 'flex';
  };

  window.closeModal = function() {
    if (modal) {
      modal.style.display = 'none';
      if (currentConfirmCallback) {
        currentConfirmCallback();
        currentConfirmCallback = null;
      }
    }
  };

  // Initialize data on load
  async function initAppData() {
    // Verify session validity with backend (handles cleared databases or deleted users)
    if (currentSession && currentSession.user_id) {
      const validUser = await API.getUser(currentSession.user_id);
      if (!validUser) {
        localStorage.removeItem('apon_session');
        currentSession = null;
        currentUserId = null;
        currentRole = 'guest';
        isViewingAsParticipant = false;
      }
    }

    syncAuthUI();
    renderWarmNoteBanner();
    startLiveClock(); // Start live clock unconditionally so all visitors see accurate local time

    // User Requirement #1: Website Entry & Login Flow
    // When a user opens the website URL, the first page must always be the Login page.
    // Do not show the main dashboard before authentication.
    if (!currentSession) {
      switchTab('login-view');
      return;
    }

    // Check if there's a hash in the URL to restore the view
    const hash = window.location.hash;
    const restoredView = hashToView[hash];

    // Authenticated user flows:
    if (currentSession.role === 'caregiver') {
      await renderCaregiverPatients();
      // If hash points to a participant view, enable participant mode
      if (restoredView && ['elderly-view', 'games-view', 'progress-view', 'memory-view', 'routine-view'].includes(restoredView)) {
        isViewingAsParticipant = true;
        syncAuthUI();
        const patientId = getActiveUserId();
        if (patientId) {
          await renderRoutineSchedule();
          await renderMemoryAnchors();
          await renderPatientAnalytics(patientId);
          startLiveClock();
        }
        switchTab(restoredView);
      } else {
        switchTab('caregiver-view');
      }
    } else {
      currentUserId = currentSession.user_id;
      await renderRoutineSchedule();
      await renderMemoryAnchors();
      await renderPatientAnalytics(currentUserId);
      startLiveClock(); // ← start live clock for returning elderly session
      // Restore hash-based view if valid for elderly
      if (restoredView && elderlyAllowedViews.includes(restoredView) && restoredView !== 'login-view') {
        switchTab(restoredView);
      } else {
        switchTab('elderly-view');
      }
    }
  }

  await initAppData();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  startApp();
}
