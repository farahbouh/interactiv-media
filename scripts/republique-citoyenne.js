// Génère et télécharge un PDF de l'affiche République citoyenne.
document.getElementById('downloadPdfBtn').addEventListener('click', function () {
	const { jsPDF } = window.jspdf;
	const doc = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });

	const img = new Image();
	img.crossOrigin = 'anonymous';
	img.src = 'images/republique-citoyenne-affiche.webp';

	img.onload = function () {
		const canvas = document.createElement('canvas');
		canvas.width = img.naturalWidth;
		canvas.height = img.naturalHeight;
		canvas.getContext('2d').drawImage(img, 0, 0);
		const imgData = canvas.toDataURL('image/png');

		const pageWidth = doc.internal.pageSize.getWidth();
		const pageHeight = doc.internal.pageSize.getHeight();
		const margin = 10;
		const maxWidth = pageWidth - margin * 2;
		const maxHeight = pageHeight - margin * 2;

		const ratio = img.naturalWidth / img.naturalHeight;
		let renderWidth = maxWidth;
		let renderHeight = renderWidth / ratio;

		if (renderHeight > maxHeight) {
			renderHeight = maxHeight;
			renderWidth = renderHeight * ratio;
		}

		const x = (pageWidth - renderWidth) / 2;
		const y = (pageHeight - renderHeight) / 2;

		doc.addImage(imgData, 'PNG', x, y, renderWidth, renderHeight);
		doc.save('republique-citoyenne-interactiv-media.pdf');
	};

	img.onerror = function () {
		alert("Erreur lors du chargement de l'image pour la génération du PDF.");
	};
});
