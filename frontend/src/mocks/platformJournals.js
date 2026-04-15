export const platformJournals = [
  {
    id: 'lancet',
    name: 'The Lancet',
    description: 'The world\'s leading independent general medical journal.',
    coverImage: '/assets/journals/lancet-cover.jpg',
    color: '#005696', // Lancet Blue
    issn: '0140-6736',
    impactFactor: '202.731',
    editorInChief: 'Richard Horton',
    subjects: ['General Medicine', 'Clinical Medicine', 'Public Health'],
    acceptsTransfers: true,
    relatedJournals: ['lancet-oncology', 'lancet-neurology']
  },
  {
    id: 'lancet-oncology',
    name: 'The Lancet Oncology',
    description: 'Clinical oncology research and reviews.',
    coverImage: '/assets/journals/oncology-cover.jpg',
    color: '#B71C1C', // Reddish
    issn: '1470-2045',
    impactFactor: '54.433',
    editorInChief: 'David Collingridge',
    subjects: ['Oncology', 'Cancer Research'],
    acceptsTransfers: true,
    relatedJournals: ['lancet']
  },
  {
    id: 'lancet-neurology',
    name: 'The Lancet Neurology',
    description: 'The most authoritative source of news and analysis in neurology.',
    coverImage: '/assets/journals/neurology-cover.jpg',
    color: '#F57F20', // Orange
    issn: '1474-4422',
    impactFactor: '59.939',
    editorInChief: 'Elena Becker-Barroso',
    subjects: ['Neurology', 'Neuroscience'],
    acceptsTransfers: true,
    relatedJournals: ['lancet']
  }
];
