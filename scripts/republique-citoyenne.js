// Génère et télécharge un PDF du contenu de la page République citoyenne
document.getElementById('downloadPdfBtn').addEventListener('click', function () {
	const element = document.getElementById('pdf-content');
	const options = {
		margin: 10,
		filename: 'republique-citoyenne-interactiv-media.pdf',
		image: { type: 'jpeg', quality: 0.98 },
		html2canvas: { scale: 2 },
		jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
	};
	html2pdf().set(options).from(element).save();
});
