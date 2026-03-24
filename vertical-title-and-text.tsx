const layoutId = "vertical-title-and-text";
const layoutName = "Vertical Title and Text";
const layoutDescription = "A slide with vertical title on the left and content on the right";

const Schema = z.object({
  title: z.string().min(1).default("Vertical Title"),
  content: z.string().default("Body content")
});

const dynamicSlideLayout = ({ data }: { data: any }) => {
  const {
    title = 'Vertical Title',
    content = 'Vertical text layout content'
  } = data || {};

  const contentArray = Array.isArray(content) ? content : [content];

  return (
    <div 
      style={{
        width: '100%',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#FFFFFF'
      }}
      data-layout="vertical-title-and-text"
    >
      {/* Purple Top Bar */}
      <div
        style={{
          backgroundColor: '#8F1A95',
          height: '60px',
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          paddingLeft: '40px',
          paddingRight: '40px'
        }}
      >
        <h1
          style={{
            color: '#FFFFFF',
            fontFamily: 'Calibri Light, Calibri, sans-serif',
            fontSize: '32px',
            fontWeight: 300,
            margin: 0,
            letterSpacing: '0.5px'
          }}
        >
          {title}
        </h1>
      </div>

      {/* Content Area */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '40px',
          backgroundColor: '#FFFFFF',
          borderLeft: '5px solid #8F1A95'
        }}
      >
        {typeof content === 'string' && !Array.isArray(content) ? (
          <p
            style={{
              color: '#44546A',
              fontFamily: 'Calibri, sans-serif',
              fontSize: '18px',
              lineHeight: '1.6',
              margin: '0'
            }}
          >
            {content}
          </p>
        ) : (
          <ul
            style={{
              color: '#44546A',
              fontFamily: 'Calibri, sans-serif',
              fontSize: '18px',
              lineHeight: '1.8',
              margin: '0',
              paddingLeft: '20px',
              listStyleType: 'disc'
            }}
          >
            {contentArray.map((item: string, idx: number) => (
              <li
                key={idx}
                style={{
                  marginBottom: '12px'
                }}
              >
                {item}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

