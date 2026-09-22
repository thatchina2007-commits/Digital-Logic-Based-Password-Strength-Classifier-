/**
 * main.js
 * EC2201 Digital Logic Password Strength Classifier
 * Handles real-time input evaluation, logic circuit animation, interactive switches,
 * password visibility toggling, and report copying.
 */

document.addEventListener('DOMContentLoaded', () => {
    initPasswordClassifier();
});

function initPasswordClassifier() {
    const passwordInput = document.getElementById('passwordInput');
    const toggleVisibilityBtn = document.getElementById('toggleVisibilityBtn');
    
    if (toggleVisibilityBtn && passwordInput) {
        toggleVisibilityBtn.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            toggleVisibilityBtn.innerHTML = isPassword 
                ? '<i class="fa-solid fa-eye-slash"></i>' 
                : '<i class="fa-solid fa-eye"></i>';
        });
    }

    if (passwordInput) {
        // Immediate evaluation on input
        passwordInput.addEventListener('input', () => {
            evaluatePasswordLive(passwordInput.value);
        });

        // Trigger on load if initial text exists
        if (passwordInput.value) {
            evaluatePasswordLive(passwordInput.value);
        }
    }

    // Sample buttons
    const sampleBtns = document.querySelectorAll('.btn-sample-pwd');
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const sample = btn.getAttribute('data-sample');
            if (passwordInput && sample !== null) {
                passwordInput.value = sample;
                evaluatePasswordLive(sample);
            }
        });
    });
}

/**
 * Sends password to backend API or runs local evaluation
 */
async function evaluatePasswordLive(password) {
    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        updateClassifierUI(data);

        // If Truth Table component is present, highlight row
        if (typeof highlightTruthTableRow === 'function') {
            highlightTruthTableRow(data.minterm_idx);
        }
    } catch (err) {
        console.error('Error evaluating password:', err);
    }
}

/**
 * Updates DOM with digital logic circuit trace and classification
 */
function updateClassifierUI(data) {
    const attrs = data.attributes;
    const circuit = data.circuit_trace;
    const bits = circuit.bits;

    // 1. Update 5 Binary Variable Chips & LEDs
    const varKeys = ['A', 'B', 'C', 'D', 'E'];
    varKeys.forEach(key => {
        const val = attrs[key];
        const led = document.getElementById(`led-${key}`);
        const bitVal = document.getElementById(`val-${key}`);
        const chip = document.getElementById(`chip-${key}`);

        if (led) {
            led.className = `logic-led ${val === 1 ? 'led-high' : 'led-low'}`;
        }
        if (bitVal) {
            bitVal.textContent = val;
            bitVal.className = val === 1 ? 'text-info fw-bold' : 'text-secondary';
        }
        if (chip) {
            if (val === 1) chip.classList.add('active');
            else chip.classList.remove('active');
        }
    });

    // 2. Update Intermediate Circuit Gate Values (FA1, HA1, HA2, FA2)
    const stage1 = circuit.stage1;
    const stage2 = circuit.stage2;
    const stage3 = circuit.stage3;

    setElemText('gate-fa1-sum', stage1.FA1.Sum);
    setElemText('gate-fa1-cout', stage1.FA1.Carry);
    setElemText('gate-ha1-sum', stage1.HA1.Sum);
    setElemText('gate-ha1-cout', stage1.HA1.Carry);

    setElemText('gate-ha2-s0', stage2.HA2.S0);
    setElemText('gate-ha2-c3', stage2.HA2.C3);

    setElemText('gate-fa2-s1', stage3.FA2.S1);
    setElemText('gate-fa2-s2', stage3.FA2.S2);

    // 3. Update 3-Bit Output Bits S2, S1, S0
    setElemText('bit-s2', bits.S2);
    setElemText('bit-s1', bits.S1);
    setElemText('bit-s0', bits.S0);
    setElemText('total-score-val', `${data.score} / 5`);
    setElemText('minterm-badge', data.minterm);
    setElemText('binary-vector-val', `${attrs.A}${attrs.B}${attrs.C}${attrs.D}${attrs.E}`);
    setElemText('adder-binary-val', circuit.binary_output);

    // 4. Update Strength Meter & Category Badge
    const meterBar = document.getElementById('strengthMeterBar');
    const categoryBadge = document.getElementById('categoryBadge');
    const categoryDesc = document.getElementById('categoryDescription');

    if (meterBar) {
        meterBar.style.width = `${Math.max(15, data.percentage)}%`;
        meterBar.className = 'strength-meter-bar';
        if (data.category === 'Weak') meterBar.classList.add('weak');
        else if (data.category === 'Medium') meterBar.classList.add('medium');
        else if (data.category === 'Strong') meterBar.classList.add('strong');
        else if (data.category === 'Very Strong') meterBar.classList.add('very-strong');
    }

    if (categoryBadge) {
        categoryBadge.textContent = data.category;
        categoryBadge.className = '';
        if (data.category === 'Weak') categoryBadge.className = 'badge-strength-weak';
        else if (data.category === 'Medium') categoryBadge.className = 'badge-strength-medium';
        else if (data.category === 'Strong') categoryBadge.className = 'badge-strength-strong';
        else if (data.category === 'Very Strong') categoryBadge.className = 'badge-strength-very-strong';
    }

    let prevCategory = window._prevPasswordCategory || '';
    if (data.category === 'Very Strong' && prevCategory !== 'Very Strong' && typeof confetti === 'function') {
        confetti({
            particleCount: 70,
            spread: 60,
            origin: { y: 0.7 },
            colors: ['#00f2fe', '#00f5a0', '#9d4edd', '#ffffff']
        });
    }
    window._prevPasswordCategory = data.category;

    if (categoryDesc) {
        categoryDesc.textContent = data.description;
    }

    // 5. Update Missing Criteria / Rule Explanation Panel
    const recommendationsList = document.getElementById('recommendationsList');
    if (recommendationsList) {
        recommendationsList.innerHTML = '';
        if (data.missing_criteria.length === 0) {
            const li = document.createElement('li');
            li.className = 'text-success small mb-1';
            li.innerHTML = '<i class="fa-solid fa-circle-check me-2"></i><strong>All Logic Criteria Satisfied!</strong> Optimal entropy achieved.';
            recommendationsList.appendChild(li);
        } else {
            data.missing_criteria.forEach(item => {
                const li = document.createElement('li');
                li.className = 'text-warning small mb-1';
                li.innerHTML = `<i class="fa-solid fa-triangle-exclamation me-2"></i>${item}`;
                recommendationsList.appendChild(li);
            });
        }
    }
}

function setElemText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

/**
 * Copies evaluation summary as text for viva presentation or lab report
 */
function copyEvaluationReport() {
    const pwdInput = document.getElementById('passwordInput');
    const scoreVal = document.getElementById('total-score-val')?.textContent || '';
    const catBadge = document.getElementById('categoryBadge')?.textContent || '';
    const binVector = document.getElementById('binary-vector-val')?.textContent || '';
    const adderBin = document.getElementById('adder-binary-val')?.textContent || '';
    const minterm = document.getElementById('minterm-badge')?.textContent || '';

    const text = `=== EC2201 DIGITAL LOGIC PASSWORD CLASSIFICATION REPORT ===
Password Length: ${pwdInput ? pwdInput.value.length : 0}
Binary Input Vector [A B C D E]: ${binVector}
Truth Table Minterm: ${minterm}
Adder Network Output (S2 S1 S0): ${adderBin}
Total Logic Score: ${scoreVal}
Final Classification: ${catBadge}
Timestamp: ${new Date().toLocaleString()}
=============================================================`;

    navigator.clipboard.writeText(text).then(() => {
        alert('Evaluation Report successfully copied to clipboard!');
    }).catch(err => {
        console.error('Clipboard copy failed:', err);
    });
}
