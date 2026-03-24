const layoutId = "vertical-title-and-text";
const layoutName = "Vertical Title and Text";
const layoutDescription = "Content with vertical title on the right";

const Schema = z.object({
  title: z.string().default('Slide Title'),
  content: z.array(z.string()).default([]).describe('Content bullet points'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo')
});

const dynamicSlideLayout = ({ data }) => {
  const { title = 'Slide Title', content = [], show_logo = true } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    boxSizing: 'border-box'
  };

  const mainStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column'
  };

  const logoContainerStyle = {
    padding: '15px 30px',
    display: 'flex',
    justifyContent: 'flex-start',
    borderBottom: '2px solid #8F1A95'
  };

  const logoStyle = {
    height: '30px'
  };

  const contentStyle = {
    flex: 1,
    padding: '40px 50px'
  };

  const listStyle = {
    fontSize: '22px',
    fontFamily: 'Calibri, sans-serif',
    color: '#333333',
    lineHeight: '1.7',
    margin: 0,
    paddingLeft: '25px'
  };

  const listItemStyle = {
    marginBottom: '15px'
  };

  const sidebarStyle = {
    width: '80px',
    backgroundColor: '#8F1A95',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px 10px'
  };

  const titleStyle = {
    fontSize: '28px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    writingMode: 'vertical-rl',
    textOrientation: 'mixed',
    margin: 0,
    textAlign: 'center'
  };

  return (
    <div style={containerStyle} data-layout="vertical-title-and-text">
      <div style={mainStyle}>
        {show_logo && (
          <div style={logoContainerStyle}>
            <img 
              src="/images/usdaw-template-new/usdaw-logo-official.svg" 
              alt="USDAW" 
              style={logoStyle}
            />
          </div>
        )}
        <div style={contentStyle}>
          <ul style={listStyle}>
            {content.map((item, idx) => <li key={idx} style={listItemStyle}>{item}</li>)}
          </ul>
        </div>
      </div>
      <div style={sidebarStyle}>
        <h1 style={titleStyle}>{title}</h1>
      </div>
    </div>
  );
};

