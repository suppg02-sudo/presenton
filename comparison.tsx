const layoutId = "comparison";
const layoutName = "Comparison";
const layoutDescription = "A slide for comparing two options with title and feature lists";

const Schema = z.object({
  title: z.string().min(1).default("Comparison"),
  left_title: z.string().default("Left Option"),
  left_items: z.array(z.string()).default(["Item one", "Item two", "Item three"]),
  right_title: z.string().default("Right Option"),
  right_items: z.array(z.string()).default(["Item one", "Item two", "Item three"])
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Comparison',
    left_title = 'Left Option',
    left_items = ['Item one', 'Item two', 'Item three'],
    right_title = 'Right Option',
    right_items = ['Item one', 'Item two', 'Item three']
  } = data || {};

  const titleStyle = {
    backgroundColor: '#8F1A95',
    color: '#FFFFFF',
    padding: '40px',
    textAlign: 'center',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontSize: '36px',
    fontWeight: 'bold',
    margin: '0',
    width: '100%',
    boxSizing: 'border-box'
  };

  const containerStyle = {
    display: 'flex',
    width: '100%',
    height: 'calc(100vh - 120px)',
    margin: '0',
    padding: '0'
  };

  const leftColumnStyle = {
    flex: '1',
    backgroundColor: '#E7E6E6',
    padding: '40px',
    overflowY: 'auto',
    boxSizing: 'border-box',
    borderRight: '3px solid #44546A'
  };

  const rightColumnStyle = {
    flex: '1',
    backgroundColor: '#FFFFFF',
    padding: '40px',
    overflowY: 'auto',
    boxSizing: 'border-box'
  };

  const columnHeaderStyle = {
    color: '#8F1A95',
    fontFamily: 'Calibri Light, Calibri, sans-serif',
    fontSize: '24px',
    fontWeight: 'bold',
    marginTop: '0',
    marginBottom: '20px',
    paddingBottom: '12px',
    borderBottom: '2px solid #8F1A95'
  };

  const listStyle = {
    listStyle: 'none',
    padding: '0',
    margin: '0'
  };

  const listItemStyle = {
    color: '#44546A',
    fontFamily: 'Calibri, sans-serif',
    fontSize: '16px',
    padding: '12px 0',
    borderBottom: '1px solid #E7E6E6',
    margin: '0'
  };

  return (
    <div style={{ width: '100%', height: '100vh', margin: '0', padding: '0', boxSizing: 'border-box' }} data-layout="comparison">
      <div style={titleStyle}>{title}</div>
      <div style={containerStyle}>
        <div style={leftColumnStyle}>
          <h3 style={columnHeaderStyle}>{left_title}</h3>
          <ul style={listStyle}>
            {left_items.map((item, idx) => (
              <li key={idx} style={listItemStyle}>✓ {item}</li>
            ))}
          </ul>
        </div>
        <div style={rightColumnStyle}>
          <h3 style={columnHeaderStyle}>{right_title}</h3>
          <ul style={listStyle}>
            {right_items.map((item, idx) => (
              <li key={idx} style={listItemStyle}>✓ {item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

