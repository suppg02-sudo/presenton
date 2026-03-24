const layoutId = "two-content";
const layoutName = "Two Content";
const layoutDescription = "Side-by-side content columns";

const Schema = z.object({
  title: z.string().default('Slide Title'),
  left_title: z.string().optional().describe('Left column heading'),
  left_content: z.array(z.string()).default([]).describe('Left column bullet points'),
  right_title: z.string().optional().describe('Right column heading'),
  right_content: z.array(z.string()).default([]).describe('Right column bullet points'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Slide Title',
    left_title,
    left_content = [],
    right_title,
    right_content = [],
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
    gap: '40px'
  };

  const columnStyle = {
    flex: 1
  };

  const columnTitleStyle = {
    fontSize: '24px',
    fontFamily: 'Calibri, sans-serif',
    color: '#8F1A95',
    marginBottom: '15px',
    borderBottom: '2px solid #8F1A95',
    paddingBottom: '10px'
  };

  const listStyle = {
    fontSize: '20px',
    fontFamily: 'Calibri, sans-serif',
    color: '#333333',
    lineHeight: '1.6',
    margin: 0,
    paddingLeft: '25px'
  };

  const listItemStyle = {
    marginBottom: '10px'
  };

  const renderList = (items) => (
    <ul style={listStyle}>
      {items.map((item, idx) => <li key={idx} style={listItemStyle}>{item}</li>)}
    </ul>
  );

  return (
    <div style={containerStyle} data-layout="two-content">
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
        <div style={columnStyle}>
          {left_title && <h2 style={columnTitleStyle}>{left_title}</h2>}
          {renderList(left_content)}
        </div>
        <div style={columnStyle}>
          {right_title && <h2 style={columnTitleStyle}>{right_title}</h2>}
          {renderList(right_content)}
        </div>
      </div>
    </div>
  );
};

