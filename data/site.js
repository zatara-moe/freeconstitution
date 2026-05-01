module.exports = {
  title: "Free Constitution",
  tagline: "Read your Constitution. Know your rights.",
  buildDate: (() => {
    const d = new Date();
    const months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  })()
};
