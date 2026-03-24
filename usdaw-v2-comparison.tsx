const layoutId = "comparison";
const layoutName = "Comparison";
const layoutDescription = "Compare two items side by side";

const Schema = z.object({
  title: z.string().default('Comparison'),
  left_label: z.string().default('Option A'),
  left_items: z.array(z.string()).default([]).describe('Left side items'),
  right_label: z.string().default('Option B'),
  right_items: z.array(z.string()).default([]).describe('Right side items'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Comparison',
    left_label = 'Option A',
    left_items = [],
    right_label = 'Option B',
    right_items = [],
    show_logo = true
  } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box'
  };

  const headerStyle = {
    backgroundColor: '#8F1A95',
    padding: '20px 40px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const titleStyle = {
    fontSize: '32px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: 0
  };

  const logoStyle = {
    height: '35px'
  };

  const columnsStyle = {
    flex: 1,
    display: 'flex',
    padding: '30px 40px',
    gap: '30px'
  };

  const leftBoxStyle = {
    flex: 1,
    backgroundColor: '#F8F8F8',
    borderRadius: '8px',
    padding: '25px'
  };

  const rightBoxStyle = {
    flex: 1,
    backgroundColor: '#8F1A95',
    borderRadius: '8px',
    padding: '25px'
  };

  const labelStyle = {
    fontSize: '22px',
    fontFamily: 'Calibri, sans-serif',
    margin: '0 0 15px 0',
    textAlign: 'center'
  };

  const leftLabelStyle = {
    ...labelStyle,
    color: '#8F1A95'
  };

  const rightLabelStyle = {
    ...labelStyle,
    color: '#FFFFFF'
  };

  const listStyle = {
    fontSize: '18px',
    fontFamily: 'Calibri, sans-serif',
    lineHeight: '1.6',
    margin: 0,
    paddingLeft: '20px'
  };

  const leftListStyle = {
    ...listStyle,
    color: '#333333'
  };

  const rightListStyle = {
    ...listStyle,
    color: '#FFFFFF'
  };

  const listItemStyle = {
    marginBottom: '8px'
  };

  const renderItems = (items, isRight) => (
    <ul style={isRight ? rightListStyle : leftListStyle}>
      {items.map((item, idx) => <li key={idx} style={listItemStyle}>{item}</li>)}
    </ul>
  );

  return (
    <div style={containerStyle} data-layout="comparison">
      <div style={headerStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {show_logo && (
          <img 
            src="/images/usdaw-template-new/usdaw-logo-white.svg" 
            alt="USDAW" 
            style={logoStyle}
          />
        )}
      </div>
      <div style={columnsStyle}>
        <div style={leftBoxStyle}>
          <h2 style={leftLabelStyle}>{left_label}</h2>
          {renderItems(left_items, false)}
        </div>
        <div style={rightBoxStyle}>
          <h2 style={rightLabelStyle}>{right_label}</h2>
          {renderItems(right_items, true)}
        </div>
      </div>
    </div>
  );
};

