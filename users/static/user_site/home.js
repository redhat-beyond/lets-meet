const toggle = document.querySelector('.toggle');
const calender = document.querySelector('.calender');

toggle.addEventListener('click', (e)=> {
	toggleClass(calender, 'cal-view');
});

let toggleClass = (el, className) => {
	if (el.classList) {
		el.classList.toggle(className);
	} else {
		let classes = el.className.split(' ');
		const existingIndex = classes.indexOf(className);

		if (existingIndex >= 0) {
		classes.splice(existingIndex, 1);
		} else {
		classes.push(className);
		}

		el.className = classes.join(' ');
	}
};
