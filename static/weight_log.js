//Creates a visualizer of the BMI scale
//BMI scale goes from <18 (underweight) to >45 (severely obese)
//For representation, BMI scale will go as low as 0 and as high as 60
//For representation, multiply each entry by SCALING_FACTOR.

bmi_visualizer = document.querySelector(".bmi-visualizer");
bmi_category_span = document.getElementById("bmi-category-span");

SCALING_FACTOR = 17;

user_bmi_category = null;

class BMICategory {
    constructor(min, max, name, color) {
        this.min = min;
        this.max = max;
        this.name = name;
        this.color = color;
    }
};

const underweight = new BMICategory(0, 18, "Underweight", "#84acd1");
const normal_weight = new BMICategory(18, 25, "Normal", "#3bcc62");
const overweight = new BMICategory(25, 30, "Overweight", "#e7da31");
const obese = new BMICategory(30, 45, "Obese", "#f57c2d");
const severely_obese = new BMICategory(45, 60, "Severely Obese", "#f15052");
const categories = [underweight, normal_weight, overweight, obese, severely_obese];

function renderBMIScale(current_bmi){
    for (i = 0; i < categories.length; i++) {
        const bmiVisualizerWrapper = document.createElement("div");
        const bmiTextWrapper = document.createElement("div");
        const bmiColorWrapper = document.createElement("div");
        width_diff = categories[i].max - categories[i].min;
        const bmiTextDiv = document.createElement("div");
        bmiTextDiv.innerHTML = categories[i].min + "-" + categories[i].max;
        bmiTextDiv.width = width_diff * SCALING_FACTOR + "px";
        bmiTextDiv.style.textAlign = "center";
        const bmiColorDiv = document.createElement("div");
        bmiColorDiv.style.width = width_diff * SCALING_FACTOR + "px";
        bmiColorDiv.style.height = 100 + "px";
        bmiColorDiv.style.backgroundColor = categories[i].color;
        bmiColorDiv.innerHTML = categories[i].name;
        bmiColorDiv.style.textAlign = "center";

        bmiTextWrapper.appendChild(bmiTextDiv);
        bmiColorWrapper.appendChild(bmiColorDiv);

        if (current_bmi >= categories[i].min && current_bmi <= categories[i].max)
            {
                user_bmi_category = categories[i];
                bmi_padding_left = ((current_bmi - categories[i].min) / (categories[i].max - categories[i].min) * width_diff * SCALING_FACTOR);
                const bmiDivLine = document.createElement("div");
                bmiDivLine.style.height = 100 + "px";
                bmiDivLine.style.top = "-24px";
                bmiDivLine.style.width = 2 + "px";
                bmiDivLine.style.backgroundColor = "black";
                bmiDivLine.style.zIndex = "1";
                bmiDivLine.style.position = "relative";
                bmiDivLine.style.left = bmi_padding_left + "px";
                bmiColorDiv.appendChild(bmiDivLine);
            }

        bmiVisualizerWrapper.appendChild(bmiTextWrapper);
        bmiVisualizerWrapper.appendChild(bmiColorWrapper);
        bmi_visualizer.appendChild(bmiVisualizerWrapper);
    }
    bmi_category_span.innerHTML = "Category: " + getUserBMICategory().name;
    bmi_category_span.style.color = getUserBMICategory().color;
};

function getUserBMICategory() {
    return user_bmi_category;
}

function resetValues(id) {
    weight_input = document.getElementById("weightinput" + id);
    date_input = document.getElementById("dateinput" + id);
    hours_input = document.getElementById("hoursinput" + id);
    minutes_input = document.getElementById("minutesinput" + id);
    current_log = null;
    weight_entries = JSON.parse(weight_entries_json);
    for (i = 0; i < weight_entries.length; i++) {
        if(weight_entries[i][0] == id) {
            current_log = weight_entries[i];
        }
    }
    if (!current_log) {
        return;
    }
    weight_input.value = current_log[2];
    date_input.value = current_log[3].slice(6, 10) + "-" + current_log[3].slice(3, 5) + "-" + current_log[3].slice(0, 2);
    hours_input.value = current_log[4].slice(0, 2);
    minutes_input.value = current_log[4].slice(3, 5);
}