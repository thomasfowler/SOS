// Before the page unloads (e.g., when the sort action is triggered), save the scroll position to sessionStorage
window.onbeforeunload = function() {
    sessionStorage.setItem('scrollPosition', window.scrollY || document.documentElement.scrollTop);
};

// When the page loads, retrieve the scroll position and apply it
document.addEventListener('DOMContentLoaded', function() {
    var scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('scrollPosition'); // Clear the stored position
    }
});
