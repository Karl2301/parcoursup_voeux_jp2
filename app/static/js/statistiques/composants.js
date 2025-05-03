document.addEventListener("DOMContentLoaded", async function () {
    try {
        // Déclaration des variables pour les graphiques
        let voeuxTotalParClasseChart, moyenneVoeuxParEleveChart, voeuxParTypeParClasseChart,
            repartitionVoeuxParVilleChart, top10FormationsChart, repartitionTypesFormationChart,
            voeuxParEtablissementChart, elevesParFormationChart, voeuxParSemaineChart;

        // Fonction pour initialiser ou mettre à jour les graphiques
        function updateCharts(stats) {
            // 1. Vœux total par classe
            if (!voeuxTotalParClasseChart) {
                const ctx1 = document.getElementById('voeuxTotalParClasse').getContext('2d');
                voeuxTotalParClasseChart = new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(stats.voeux_total_par_classe),
                        datasets: [{
                            label: 'Total Vœux par Classe',
                            data: Object.values(stats.voeux_total_par_classe),
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            } else {
                voeuxTotalParClasseChart.data.labels = Object.keys(stats.voeux_total_par_classe);
                voeuxTotalParClasseChart.data.datasets[0].data = Object.values(stats.voeux_total_par_classe);
                voeuxTotalParClasseChart.update();
            }

            // 2. Moyenne de vœux par élève
            if (!moyenneVoeuxParEleveChart) {
                const ctx2 = document.getElementById('moyenneVoeuxParEleve').getContext('2d');
                moyenneVoeuxParEleveChart = new Chart(ctx2, {
                    type: 'line',
                    data: {
                        labels: Object.keys(stats.moyenne_voeux_par_eleve_par_classe),
                        datasets: [{
                            label: 'Moyenne de Vœux par Élève',
                            data: Object.values(stats.moyenne_voeux_par_eleve_par_classe),
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 2,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            } else {
                moyenneVoeuxParEleveChart.data.labels = Object.keys(stats.moyenne_voeux_par_eleve_par_classe);
                moyenneVoeuxParEleveChart.data.datasets[0].data = Object.values(stats.moyenne_voeux_par_eleve_par_classe);
                moyenneVoeuxParEleveChart.update();
            }

            // 3. Vœux par type par classe
            if (!voeuxParTypeParClasseChart) {
                const ctx3 = document.getElementById('voeuxParTypeParClasse').getContext('2d');
                const classes = Object.keys(stats.voeux_par_type_par_classe);
                const types = Object.keys(stats.voeux_par_type_par_classe[classes[0]]);
                const colors = [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(75, 85, 106, 0.6)',
                    'rgba(140, 86, 75, 0.6)',
                    'rgba(231, 233, 237, 0.6)',
                    'rgba(220, 20, 60, 0.6)'
                ];
                const datasets = types.map((type, index) => ({
                    label: type,
                    data: classes.map(cls => stats.voeux_par_type_par_classe[cls][type]),
                    backgroundColor: colors[index % colors.length]
                }));

                voeuxParTypeParClasseChart = new Chart(ctx3, {
                    type: 'bar',
                    data: {
                        labels: classes,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { stacked: true },
                            y: { beginAtZero: true, stacked: true }
                        }
                    }
                });
            } else {
                const classes = Object.keys(stats.voeux_par_type_par_classe);
                const types = Object.keys(stats.voeux_par_type_par_classe[classes[0]]);
                voeuxParTypeParClasseChart.data.labels = classes;
                voeuxParTypeParClasseChart.data.datasets.forEach((dataset, index) => {
                    dataset.data = classes.map(cls => stats.voeux_par_type_par_classe[cls][types[index]]);
                });
                voeuxParTypeParClasseChart.update();
            }

            // 4. Répartition des vœux par ville
            if (!repartitionVoeuxParVilleChart) {
                const ctx4 = document.getElementById('repartitionVoeuxParVille').getContext('2d');
                repartitionVoeuxParVilleChart = new Chart(ctx4, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(stats.repartition_voeux_par_ville),
                        datasets: [{
                            data: Object.values(stats.repartition_voeux_par_ville),
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)',
                                'rgba(75, 85, 106, 0.6)',
                                'rgba(140, 86, 75, 0.6)',
                                'rgba(231, 233, 237, 0.6)',
                                'rgba(220, 20, 60, 0.6)'
                            ]
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });
            } else {
                repartitionVoeuxParVilleChart.data.labels = Object.keys(stats.repartition_voeux_par_ville);
                repartitionVoeuxParVilleChart.data.datasets[0].data = Object.values(stats.repartition_voeux_par_ville);
                repartitionVoeuxParVilleChart.update();
            }

            // 5. Top 10 des formations les plus demandées
            if (!top10FormationsChart) {
              const ctx5 = document.getElementById('top10Formations').getContext('2d');
              top10FormationsChart = new Chart(ctx5, {
                  type: 'bar',
                  data: {
                      labels: stats.top_10_formations.map(item => item.nom),
                      datasets: [{
                          label: 'Nombre de Vœux',
                          data: stats.top_10_formations.map(item => item.count),
                          backgroundColor: 'rgba(255, 159, 64, 0.6)'
                      }]
                  },
                  options: {
                      indexAxis: 'y',
                      responsive: true,
                      plugins: {
                          legend: { display: false },
                          tooltip: { enabled: true }
                      },
                      scales: {
                          y: { ticks: { display: false } },
                          x: { beginAtZero: true }
                      }
                  }
              });
          } else {
              top10FormationsChart.data.labels = stats.top_10_formations.map(item => item.nom);
              top10FormationsChart.data.datasets[0].data = stats.top_10_formations.map(item => item.count);
              top10FormationsChart.update();
          }

          // 6. Répartition des types de formation
          if (!repartitionTypesFormationChart) {
              const ctx6 = document.getElementById('repartitionTypesFormation').getContext('2d');
              repartitionTypesFormationChart = new Chart(ctx6, {
                  type: 'pie',
                  data: {
                      labels: Object.keys(stats.repartition_types_formation),
                      datasets: [{
                          data: Object.values(stats.repartition_types_formation),
                          backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)',
                                'rgba(75, 85, 106, 0.6)',
                                'rgba(140, 86, 75, 0.6)',
                                'rgba(231, 233, 237, 0.6)',
                                'rgba(220, 20, 60, 0.6)'
                          ]
                      }]
                  },
                  options: { responsive: true }
              });
          } else {
              repartitionTypesFormationChart.data.labels = Object.keys(stats.repartition_types_formation);
              repartitionTypesFormationChart.data.datasets[0].data = Object.values(stats.repartition_types_formation);
              repartitionTypesFormationChart.update();
          }

          // 7. Vœux par établissement
          if (!voeuxParEtablissementChart) {
              const ctx7 = document.getElementById('voeuxParEtablissement').getContext('2d');
              voeuxParEtablissementChart = new Chart(ctx7, {
                  type: 'bar',
                  data: {
                      labels: Object.keys(stats.voeux_par_etablissement),
                      datasets: [{
                          label: 'Vœux par Établissement',
                          data: Object.values(stats.voeux_par_etablissement),
                          backgroundColor: 'rgba(153, 102, 255, 0.6)'
                      }]
                  },
                  options: {
                      responsive: true,
                      plugins: {
                          legend: { display: false },
                          tooltip: { enabled: true }
                      },
                      scales: {
                          x: { ticks: { display: false } },
                          y: { beginAtZero: true }
                      }
                  }
              });
          } else {
              voeuxParEtablissementChart.data.labels = Object.keys(stats.voeux_par_etablissement);
              voeuxParEtablissementChart.data.datasets[0].data = Object.values(stats.voeux_par_etablissement);
              voeuxParEtablissementChart.update();
          }

          // 8. Nombre d'élèves par formation
          if (!elevesParFormationChart) {
              const ctx8 = document.getElementById('elevesParFormation').getContext('2d');
              elevesParFormationChart = new Chart(ctx8, {
                  type: 'bar',
                  data: {
                      labels: Object.keys(stats.eleves_par_formation),
                      datasets: [{
                          data: Object.values(stats.eleves_par_formation),
                          backgroundColor: 'rgba(255, 206, 86, 0.6)'
                      }]
                  },
                  options: {
                      responsive: true,
                      plugins: {
                          legend: { display: false },
                          tooltip: { enabled: true }
                      },
                      scales: {
                          x: { ticks: { display: false } },
                          y: { beginAtZero: true }
                      }
                  }
              });
          } else {
              elevesParFormationChart.data.labels = Object.keys(stats.eleves_par_formation);
              elevesParFormationChart.data.datasets[0].data = Object.values(stats.eleves_par_formation);
              elevesParFormationChart.update();
          }

          // 9. Évolution des vœux par semaine
          if (!voeuxParSemaineChart) {
              const ctx9 = document.getElementById('voeuxParSemaine').getContext('2d');
              voeuxParSemaineChart = new Chart(ctx9, {
                  type: 'line',
                  data: {
                      labels: Object.keys(stats.voeux_par_semaine),
                      datasets: [{
                          label: 'Vœux validés par Semaine',
                          data: Object.values(stats.voeux_par_semaine),
                          borderColor: 'rgba(54, 162, 235, 1)',
                          backgroundColor: 'rgba(54, 162, 235, 0.2)',
                          tension: 0.3,
                          fill: true
                      }]
                  },
                  options: {
                      responsive: true,
                      scales: {
                          y: { beginAtZero: true }
                      }
                  }
              });
          } else {
              voeuxParSemaineChart.data.labels = Object.keys(stats.voeux_par_semaine);
              voeuxParSemaineChart.data.datasets[0].data = Object.values(stats.voeux_par_semaine);
              voeuxParSemaineChart.update();
          }
          
        }

        // Fonction pour récupérer les données et mettre à jour les graphiques
        async function fetchAndRenderData(filterType = "all") {
            const response = await fetch(`/get_statistiques?filter_type=${filterType}`);
            const data = await response.json();
            const stats = data.statistiques;
            updateCharts(stats);
        }

        // Charger les données initiales
        await fetchAndRenderData();

        // Ajouter un gestionnaire d'événements pour le changement de filtre
        const filterVoeuxSelect = document.getElementById('filterVoeux');
        filterVoeuxSelect.addEventListener('change', async function () {
            const filterType = filterVoeuxSelect.value;
            await fetchAndRenderData(filterType);
        });
    } catch (error) {
        console.error("Erreur lors de la récupération ou de l'affichage des statistiques :", error);
    }
});

function downloadChartData(chartId, fileName) {
    // Récupérer le graphique à partir de son ID
    const chart = Chart.getChart(chartId);
    if (!chart) {
        console.error(`Graphique avec l'ID ${chartId} introuvable.`);
        return;
    }

    // Extraire les données du graphique
    const labels = chart.data.labels;
    const datasets = chart.data.datasets;

    // Préparer les données pour Excel
    const data = [];
    data.push(["Categorie", ...datasets.map(dataset => dataset.label)]); // En-têtes
    labels.forEach((label, index) => {
        const row = [label];
        datasets.forEach(dataset => {
            row.push(dataset.data[index]);
        });
        data.push(row);
    });

    // Créer une feuille Excel avec SheetJS
    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Données");

    // Télécharger le fichier Excel avec encodage UTF-16LE
    const options = { bookType: "xlsx", type: "array", compression: true };
    const excelBuffer = XLSX.write(workbook, options);
    const blob = new Blob([new Uint8Array(excelBuffer)], { type: "application/octet-stream;charset=utf-16le" });

    // Créer un lien pour le téléchargement
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
}


document.addEventListener('DOMContentLoaded', function () {
    const socket = io({
        reconnection: true,              // ✅ autorise la reconnexion automatique
        reconnectionAttempts: 5,         // ✅ nombre de tentatives
        reconnectionDelay: 1000,         // ✅ délai entre chaque tentative
        autoConnect: true,               // se connecte automatiquement
    });

    // Récupérer le cookie session_cookie
    const sessionCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('session_cookie='))
        ?.split('=')[1];

    if (sessionCookie) {
        console.log('Envoi du cookie session_cookie au serveur WebSocket');

        // Lorsque la connexion WebSocket est prête
        socket.on('connect', () => {
            socket.emit('join', { session_cookie: sessionCookie });
        });

    } else {
        console.warn("Aucun cookie 'session_cookie' trouvé");
    }

    // Détecter la déconnexion
    socket.on('disconnect', function () {
        console.log('Déconnecté du serveur WebSocket');
    });
});