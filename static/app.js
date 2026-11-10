(function () {
    "use strict";

    var form = document.getElementById("bias-form");
    if (!form) return;

    var RESISTORS = ["R1", "R2", "RC", "RE"];
    var FIELDS = ["VCC", "R1", "R2", "RC", "RE", "beta", "VBE"];

    var els = {
        errorBox: document.getElementById("error-box"),
        errorList: document.getElementById("error-list"),
        empty: document.getElementById("empty-state"),
        result: document.getElementById("result-box"),
        regionBanner: document.getElementById("region-banner"),
        regionName: document.getElementById("region-name"),
        regionDesc: document.getElementById("region-desc"),
        warningBox: document.getElementById("warning-box"),
        warningList: document.getElementById("warning-list"),
        out: {
            VB: document.getElementById("out-VB"),
            VE: document.getElementById("out-VE"),
            VC: document.getElementById("out-VC"),
            VCE: document.getElementById("out-VCE"),
            IC: document.getElementById("out-IC"),
            IB: document.getElementById("out-IB"),
            IE: document.getElementById("out-IE"),
            VTH: document.getElementById("out-VTH"),
            RTH: document.getElementById("out-RTH")
        }
    };

    function fixed(x, digits) {
        return Number.isFinite(x) ? x.toFixed(digits) : "—";
    }

    function readForm() {
        var data = new FormData(form);
        var raw = {};
        FIELDS.forEach(function (name) {
            raw[name] = String(data.get(name) == null ? "" : data.get(name)).trim();
        });
        raw.unit = data.get("unit") === "ohm" ? "ohm" : "kohm";
        return raw;
    }

    function parseInputs(raw) {
        var errors = [];
        var values = {};

        FIELDS.forEach(function (name) {
            // ยอมรับเครื่องหมาย comma/ช่องว่างเป็นตัวคั่นหลักพัน เช่น 1,000,000
            var text = raw[name].replace(/,/g, "").replace(/\s+/g, "");
            if (text === "") {
                errors.push(name + " is required");
                return;
            }
            var value = Number(text);
            if (!Number.isFinite(value)) {
                errors.push(name + " must be a finite number");
                return;
            }
            values[name] = value;
        });

        if (errors.length) return { errors: errors };

        if (values.VCC <= 0) errors.push("VCC must be greater than 0");
        RESISTORS.forEach(function (name) {
            if (values[name] <= 0) errors.push(name + " must be greater than 0");
        });
        if (values.beta <= 0) errors.push("beta must be greater than 0");
        if (values.VBE < 0.4 || values.VBE >= values.VCC) {
            errors.push("VBE must be between 0.4 V and VCC (exclusive of VCC)");
        }

        return { errors: errors, values: values };
    }

    function calculate(v, unit) {
        var VCC = v.VCC;
        var R1 = v.R1;
        var R2 = v.R2;
        var RC = v.RC;
        var RE = v.RE;
        var beta = v.beta;
        var VBE = v.VBE;

        if (unit === "kohm") {
            R1 *= 1000;
            R2 *= 1000;
            RC *= 1000;
            RE *= 1000;
        }

        // Calc A: Thevenin base-loop
        var VTH = (VCC * R2) / (R1 + R2);
        var RTH = (R1 * R2) / (R1 + R2);
        var IB = (VTH - VBE) / (RTH + (beta + 1) * RE);
        var IC = beta * IB;
        var IE = (beta + 1) * IB;
        var VE = IE * RE;
        var VB = VE + VBE;
        var VC = VCC - IC * RC;
        var VCE = VC - VE;

        var warnings = [];
        var region;
        if (IB <= 0 || IC <= 0) {
            warnings.push("Transistor likely in cutoff");
            region = "cutoff";
        } else if (VCE <= 0.2 + 1e-9) {
            warnings.push("Transistor likely in saturation (V_CE near/at saturation)");
            region = "saturation";
        } else {
            region = "active";
        }

        return {
            VTH: VTH, RTH: RTH,
            IB: IB, IC: IC, IE: IE,
            VB: VB, VE: VE, VC: VC, VCE: VCE,
            warnings: warnings, region: region
        };
    }

    function showErrors(errors) {
        els.errorList.innerHTML = "";
        errors.forEach(function (message) {
            var li = document.createElement("li");
            li.textContent = message;
            els.errorList.appendChild(li);
        });
        els.errorBox.classList.remove("hidden");
        els.result.classList.add("hidden");
        els.empty.classList.add("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function setRegion(region) {
        var text = {
            active: {
                name: "Forward Active",
                desc: "ไบอัสอยู่ในช่วง Forward Active ตามแบบจำลอง (β คงที่, VBE คงที่)"
            },
            cutoff: {
                name: "Cutoff",
                desc: "กระแสฐาน IB ≤ 0 ทรานซิสเตอร์ไม่นำกระแส ค่าที่แสดงไม่ใช่ผลจาก Forward-Active Approximation"
            },
            saturation: {
                name: "Saturation",
                desc: "VCE ≤ 0.2 V ทรานซิสเตอร์อิ่มตัว แบบจำลอง Forward-Active ใช้ไม่ได้กับผลชุดนี้"
            }
        }[region];

        els.regionBanner.className = "region region-" + region;
        els.regionName.textContent = text.name;
        els.regionDesc.textContent = text.desc;
    }

    function render(r) {
        els.errorBox.classList.add("hidden");
        els.empty.classList.add("hidden");
        els.result.classList.remove("hidden");

        setRegion(r.region);

        els.out.VB.textContent = fixed(r.VB, 3);
        els.out.VE.textContent = fixed(r.VE, 3);
        els.out.VC.textContent = fixed(r.VC, 3);
        els.out.VCE.textContent = fixed(r.VCE, 3);
        els.out.IC.textContent = fixed(r.IC * 1000, 3);
        els.out.IB.textContent = fixed(r.IB * 1e6, 2);
        els.out.IE.textContent = fixed(r.IE * 1000, 3);
        els.out.VTH.textContent = fixed(r.VTH, 3);
        els.out.RTH.textContent = fixed(r.RTH, 1);

        els.warningList.innerHTML = "";
        if (r.warnings.length) {
            r.warnings.forEach(function (message) {
                var li = document.createElement("li");
                li.textContent = message;
                els.warningList.appendChild(li);
            });
            els.warningBox.classList.remove("hidden");
        } else {
            els.warningBox.classList.add("hidden");
        }

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        var raw = readForm();
        var parsed = parseInputs(raw);
        if (parsed.errors.length) {
            showErrors(parsed.errors);
            return;
        }

        render(calculate(parsed.values, raw.unit));
    });

    form.addEventListener("reset", function () {
        window.setTimeout(function () {
            els.result.classList.add("hidden");
            els.errorBox.classList.add("hidden");
            els.empty.classList.remove("hidden");
        }, 0);
    });
})();
